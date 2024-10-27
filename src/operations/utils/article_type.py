from pathlib import Path
from rich.progress import track
import os
import re

from utils.util import read_json, write_json


def _article_no_abbrev_map(type):
    article_no_abbrev_map = {
        '篇': 'B',  # Book
        '編': 'B',  # Book
        '章': 'C',  # Chapter
        '類': 'T',  # Category
        '節': 'S',  # Section
        '款': 'P',  # Paragraph
        '目': 'I',  # Index
        '條': 'A'   # Article
    }
    return article_no_abbrev_map[type]


def _get_article_type_abbrev(text):
    # 第 3 章 -> 章
    match = re.match(r'第 \d+ (編|篇|章|類|節|款|目|條)$', text)
    if match:
        return _article_no_abbrev_map(match.group(1))
    # 第 3-1 章 -> 章
    match = re.match(r'第 \d+-\d+ (編|篇|章|類|節|款|目|條)$', text)
    if match:
        return _article_no_abbrev_map(match.group(1))
    # 1 -> 條
    match = re.match(r'^\d+$', text)
    if match:
        return _article_no_abbrev_map('條')  # Article
    # 其 1 -> 節
    match = re.match(r'其 \d+', text)
    if match:
        return _article_no_abbrev_map('節')  # Section
    # 第 3 章 第 2 類 -> 章
    match = re.match(r'第 \d+ (編|篇|章|類|節|款|目|條) 第 \d+ (編|篇|章|類|節|款|目|條)$', text)
    if match:
        return _article_no_abbrev_map(match.group(1))
    # 第 3 第 2 類 -> 章
    match = re.match(r'第 \d+ 第 \d+ (編|篇|章|類|節|款|目|條)$', text)
    if match:
        return _article_no_abbrev_map('章')


def assign_article_type(law_operation_history_folder):
    for pcode in track(os.listdir(law_operation_history_folder), description='[bold red]Assigning article type...'):
        pcode_folder = law_operation_history_folder / pcode
        for modified_date in os.listdir(pcode_folder):
            law = read_json(law_operation_history_folder / pcode / modified_date)
            law_articles = law.get('LawArticles', [])
            for law_article in law_articles:
                article_type = law_article.get('ArticleType', '')
                article_no = law_article.get('ArticleNo', '')
                if article_type == 'X':
                    abbrev = _get_article_type_abbrev(article_no)
                    law_article['ArticleType'] = abbrev
            write_json(law_operation_history_folder / pcode, modified_date.split('.')[0], law)
