import re
from bs4 import BeautifulSoup
import cn2an


def parse_law_articles(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    law_articles = []

    # Find all div elements with class "well law-reg law-content"
    law_contents = soup.find_all("div", class_="well law-reg law-content")

    for content in law_contents:
        # Process all direct children of the content div
        for child in content.children:
            if child.name == 'div':
                if 'h3' in child.get('class', []):
                    # This is a chapter or section header
                    law_articles.append({
                        "ArticleType": "C",
                        "ArticleNo": "",
                        "ArticleContent": child.text.strip()
                    })
                elif 'row' in child.get('class', []):
                    # This is an article
                    article_no = child.find("div", class_="col-no")
                    law_article = child.find("div", class_="col-data")

                    if article_no and law_article:
                        article_content = law_article.get_text(
                            separator="\n", strip=True)
                        law_articles.append({
                            "ArticleType": "A",
                            "ArticleNo": article_no.text.strip(),
                            "ArticleContent": article_content
                        })

    return law_articles


def add_law_id_field(pcode, lnndate, law):
    return {
        'LawId': f'{pcode}_{lnndate}',
        **law
    }

def add_history_index_field(law, history_index):
    return {
        'ArticleHistoryIndex': history_index,
        **law
    }


def generalize_chapter(article):
    # 移除 ArticleContent 中的所有空白
    content = article["ArticleContent"].replace(" ", "")

    # 定義正則表達式來匹配 "第X章之Y" 或 "第X節之Y"
    chapter_pattern_special = re.compile(r'^第([一二三四五六七八九十百千]+)章之([一二三四五六七八九十百千]+)')
    section_pattern_special = re.compile(r'^第([一二三四五六七八九十百千]+)節之([一二三四五六七八九十百千]+)')
    chapter_pattern = re.compile(r'^第([一二三四五六七八九十百千]+)章')
    section_pattern = re.compile(r'^第([一二三四五六七八九十百千]+)節')

    # 檢查是否匹配 "第 X 章之 Y"
    chapter_match = chapter_pattern_special.match(content)
    if chapter_match:
        print(chapter_match.group(2))
        main_num = cn2an.cn2an(chapter_match.group(1))
        sub_num = cn2an.cn2an(chapter_match.group(2))
        article["ArticleNo"] = f"第 {main_num}-{sub_num} 章"
        article["ArticleContent"] = content[chapter_match.end():]
        return article

    # 檢查是否匹配 "第 X 節之 Y"
    section_match = section_pattern_special.match(content)
    if section_match:
        main_num = cn2an.cn2an(section_match.group(1))
        sub_num = cn2an.cn2an(section_match.group(2))
        article["ArticleType"] = "S"
        article["ArticleNo"] = f"第 {main_num}-{sub_num} 節"
        article["ArticleContent"] = content[section_match.end():]
        return article

    # 檢查是否匹配 "第 X 章"
    chapter_match = chapter_pattern.match(content)
    if chapter_match:
        main_num = cn2an.cn2an(chapter_match.group(1))
        article["ArticleNo"] = f"第 {main_num} 章"
        article["ArticleContent"] = content[chapter_match.end():]
        return article

    # 檢查是否匹配 "第 X 節"
    section_match = section_pattern.match(content)
    if section_match:
        main_num = cn2an.cn2an(section_match.group(1))
        article["ArticleType"] = "S"
        article["ArticleNo"] = f"第 {main_num} 節"
        article["ArticleContent"] = content[section_match.end():]
        return article

    return article


def generalize_chapters(law):
    articles = law.get('LawArticles', [])
    for article in articles:
        if article.get('ArticleType', '') == 'C':
            generalize_chapter(article)
    return law


def extract_history_links(html_content) -> tuple:
    # 使用 BeautifulSoup 解析 HTML 內容
    soup = BeautifulSoup(html_content, 'lxml')

    # 查找所有包含 "歷史條文" 文字的 <a> 標籤
    history_links = []
    lnndates = []

    for a_tag in soup.find_all('a', string="歷史條文"):
        href = a_tag.get('href')
        if href:
            history_links.append(href)
            lnndates.append(re.search(r'lnndate=(\d+)', href).group(1))

    return history_links, lnndates
