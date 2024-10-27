import re
import cn2an
import pymupdf
import pandas as pd
import math
import requests
from bs4 import BeautifulSoup

# "is" series functions


def _is_title_chinese_regex(text):
    return bool(re.match(r'^第[一二三四五六七八九十百千]+([編篇章類節款目條])(之[一二三四五六七八九十百千]+)?', text))


def _is_article_name(word):
    # ignore the title (法條)
    _, y0, _, y1, _, _, _, _ = word
    if 15 <= y1 - y0:
        return True
    return False


def _is_second_article_name(word):
    # ignore the title (附錄)
    _, y0, _, y1, _, _, _, _ = word
    if 15 <= y1 - y0:
        return True
    return False

# "get" series functions


def _get_vertical_doc_table_x_positions(doc):
    t_min, t_max = 842, 0
    for page in doc:
        width, height = page.rect.width, page.rect.height

        # ignore the horizontal pages (842x595)
        if width >= height:
            continue

        # process vertical pages (595x842)
        words = page.get_text("words")
        df = pd.DataFrame(words, columns=['x0', 'y0', 'x1', 'y1', 'text', 'block_no', 'line_no', 'word_no'])

        df_filtered = df[~df.apply(_is_article_name, axis=1)]
        t_min, t_max = min(df_filtered['x0'].min(), t_min), max(df_filtered['x1'].max(), t_max)

    return math.floor(t_min), math.ceil(t_max)


def _is_title_position(x0, t_left):
    diff = 5
    return t_left-diff <= x0 <= t_left+diff


def _is_header(text):
    return text == '修正條文' or text == '修正名稱'


def _is_new_article_title(text, column_name, x0, separator, y0, prev_y0):
    if column_name == 'Modified':
        t_left = separator[0]
    elif column_name == 'Current':
        t_left = separator[1]
    else:
        return False

    if _is_title_position(x0, t_left) and _is_title_chinese_regex(text) or _is_header(text):
        if y0 != prev_y0:
            return True

    return False


def _get_column_separator(t_min, t_max, portion):
    t_range = t_max - t_min
    if portion == 2:
        t1 = t_min + t_range / 2
        return [t_min, t1, t1, t_max]
    if portion == 3:
        t1 = t_min + t_range / 3
        t2 = t_min + 2 * t_range / 3
        return [t_min, t1, t2, t_max]


def _get_article_type(text):
    match = re.match(r'^第[一二三四五六七八九十百千]+([編篇章類節款目條])(之[一二三四五六七八九十百千]+)?', text)
    if match:
        type = match.group(1)
        if type == '編':
            return 'B'
        if type == '章':
            return 'C'
        if type == '節':
            return 'S'
        if type == '款':
            return 'P'
        if type == '目':
            return 'I'
        if type == '條':
            return 'A'
    if re.match(r'^修正名稱$', text):
        return 'T'
    return ''


def _get_column_name(separator, x0, x1):
    diff = 10
    t_min, t1, t2, t_max = separator
    if t_min-diff <= x0 < x1 <= t1+diff:
        return 'Modified'
    elif t1-diff <= x0 < x1 <= t2+diff:
        return 'Current'
    elif t2-diff <= x0 < x1 <= t_max+diff:
        return 'Description'
    else:
        return 'Error'


def _get_chinese_article(text):
    match = re.match(r'^(第[一二三四五六七八九十百千]+[編篇章類節款目條](?:之[一二三四五六七八九十百千]+)?)', text)
    if match:
        return match.group(1)
    return None


def _is_second_title(page):
    words = page.get_text("words")
    for word in words:
        if _is_second_article_name(word):
            return True
    return False


def _get_valid_doc(doc):
    valid_doc = []
    is_second_title = False
    for idx, page in enumerate(doc):
        width, height = page.rect.width, page.rect.height
        if is_second_title:
            continue
        if width > height:
            break
        if idx != 0 and _is_second_title(page):
            break

        valid_doc.append(page)
    return valid_doc


def _is_scan_pdf(doc):
    first_page = doc[0]
    # for word in first_page.get_text("words"):
    #     if _is_article_name(word):
    #         return False
    # return True
    if not first_page.get_text("text"):
        return True
    return False


def _is_two_columns(doc):
    match_text = ""
    first_page = doc[0]
    for word in first_page.get_text("words"):
        if len(match_text) > 7:
            break
        if _is_article_name(word):
            continue
        _, _, _, _, text, _, _, _ = word
        match_text += text
        if '條文說明' in match_text:
            return True
    return False


def process_pdf_to_json(doc, pcode, lnndate, error_pcodes):
    # global variables
    prev_raw_height = -1
    articles = []
    current_article = {
        "ArticleType": "",
        "Modified": "",
        "Current": "",
        "Description": "",
    }

    # for page in doc:
    #     for word in page.get_text("words"):
    #         print(word)
    # exit()

    # filter non-valid pages
    valid_doc = _get_valid_doc(doc)
    if len(valid_doc) != len(doc):
        error_pcodes['Appendix'].append({
            'Pcode': pcode,
            'Lnndate': lnndate,
        })

    if _is_scan_pdf(doc):
        error_pcodes['Scanned PDF'].append({
            'Pcode': pcode,
            'Lnndate': lnndate,
        })
        return articles

    if _is_two_columns(doc):
        portion = 2
        error_pcodes['Two Columns'].append({
            'Pcode': pcode,
            'Lnndate': lnndate,
        })
    else:
        portion = 3

    # get column separator
    t_min, t_max = _get_vertical_doc_table_x_positions(valid_doc)
    column_separator = _get_column_separator(t_min, t_max, portion)

    for page in valid_doc:
        # process vertical pages (595x842)
        words = page.get_text("words")
        for word in words:
            if _is_article_name(word):
                continue

            x0, raw_height, x1, _, text, _, _, _ = word

            column_name = _get_column_name(column_separator, x0, x1)
            if _is_new_article_title(text, column_name, x0, column_separator, raw_height, prev_raw_height):
                if current_article.get('Description'):
                    articles.append(current_article)
                current_article = {
                    "ArticleType": _get_article_type(text),
                    "Modified": text if column_name == 'Modified' else "",
                    "Current": text if column_name == 'Current' else "",
                    "Description": "",
                }
                prev_raw_height = raw_height
            elif column_name == 'Modified':
                current_article['Modified'] += text
            elif column_name == 'Current':
                current_article['Current'] += text
            elif column_name == 'Description':
                current_article['Description'] += text

    articles.append(current_article)
    return articles


def add_chapter_and_section_id_field(articles):
    for article in articles:
        if article['ArticleType'] != 'T':
            article['Modified'] = _get_chinese_article(article['Modified'])
            article['Current'] = _get_chinese_article(article['Current'])
    return articles


def open_pdf(pdf_path):
    return pymupdf.open(pdf_path)


def filter_article_type(articles):
    return list(filter(lambda x: x['ArticleType'] != '', articles))


def remove_pdf_in_filename(filename):
    return filename.replace('.pdf', '')


def get_order_reason(pdf_path, pcode, lnndate, error_pcodes):
    doc = open_pdf(pdf_path / pcode / lnndate)
    pdf_json = process_pdf_to_json(doc, pcode, lnndate, error_pcodes)
    pdf_json = filter_article_type(pdf_json)
    pdf_json = add_chapter_and_section_id_field(pdf_json)
    return pdf_json
