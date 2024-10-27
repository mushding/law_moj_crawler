import os
from pathlib import Path
import re
from rich.progress import track
import cn2an

from utils.util import read_json, write_json


def _transfer_ch_article_to_arabic(text):
    # 第三章 -> 第 3 章
    # 民法第三章 -> 第 3 章
    match = re.match(r'.*第(.+)(編|篇|章|類|節|款|目|條)$', text)
    if match:
        return f'第 {cn2an.cn2an(match.group(1), "smart")} {match.group(2)}'
    # 第三章之一 -> 第 3-1 章
    match = re.match(r'第(.+)(編|篇|章|類|節|款|目|條)之(.+)$', text)
    if match:
        return f'第 {cn2an.cn2an(match.group(1), "smart")}-{cn2an.cn2an(match.group(3), "smart")} {match.group(2)}'
    # 1 -> 1
    match = re.match(r'^\d+$', text)
    if match:
        return text
    # 其一 -> 其 1
    match = re.match(r'其(.+)', text)
    if match:
        return f'其 {cn2an.cn2an(match.group(1), "smart")}'
    # 第三章第二類 -> 第 3 章 第 2 類
    match = re.match(r'第(.+)(編|篇|章|類|節|款|目|條)第(.+)(編|篇|章|類|節|款|目|條)$', text)
    if match:
        return f'第 {cn2an.cn2an(match.group(1), "smart")} {match.group(2)} 第 {cn2an.cn2an(match.group(3), "smart")} {match.group(4)}'
    # 第三第二類 -> 第 3 第 2 類
    match = re.match(r'第(.+)第(.+)(編|篇|章|類|節|款|目|條)$', text)
    if match:
        return f'第 {cn2an.cn2an(match.group(1), "smart")} 第 {cn2an.cn2an(match.group(2), "smart")} {match.group(3)}'

def _is_valid_article_no(text):
    match = re.match(r'.*第 \d+(-\d+)? (編|篇|章|類|節|款|目|條)', text)
    return bool(match)

def convert_article_no(law_operation_history_folder):
    for pcode in track(os.listdir(law_operation_history_folder)):
        pcode_folder = law_operation_history_folder / pcode
        for modified_date in os.listdir(pcode_folder):
            print(f'Processing {pcode} {modified_date}...')
            law = read_json(law_operation_history_folder / pcode / modified_date)
            law_articles = law.get('LawArticles', [])
            for law_article in law_articles:
                article_no = law_article.get('ArticleNo', '')
                if not _is_valid_article_no(article_no):
                    article_no = _transfer_ch_article_to_arabic(article_no)
                    law_article['ArticleNo'] = article_no
            write_json(law_operation_history_folder / pcode, modified_date.split('.')[0], law)
