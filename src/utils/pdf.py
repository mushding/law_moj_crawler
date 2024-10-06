from bs4 import BeautifulSoup
import requests
import re
import pymupdf
import os

def extract_reason_links(html_content, pcode, abnormals) -> tuple:
    # 使用 BeautifulSoup 解析 HTML 內容
    soup = BeautifulSoup(html_content, 'lxml')

    # 查找所有包含 "條文對照表" 文字的 <a> 標籤
    reason_links = []
    dates = []

    for a_tag in soup.find_all('a', string="條文對照表"):
        href = a_tag.get('href')
        if href:
            reason_links.append(href)
            match = re.search(r'date=(\d+)', href)
            file_id_match = re.search(r'FileId=(\d+)', href)
            if match:
                dates.append(match.group(1))
            elif file_id_match:
                abnormals['No Date'].append({
                    'Pcode': pcode,
                    'FileId': file_id_match.group(1),
                })
                dates.append(file_id_match.group(1))  # 如果沒有匹配到日期，FileId 也可以作為日期

    return reason_links, dates


def get_pdf_content(url):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Cookie": "ASP.NET_SessionId=53m5byrglvro1rwuqmgo1kfx; showmode=",
        "DNT": "1",
        "Host": "law.moj.gov.tw",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Chromium";v="129", "Not=A?Brand";v="8"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"'
    }

    resp = requests.get(url, headers=headers)
    return resp.content

def is_pdf(pdf_path):
    try:
        pymupdf.open(f'{pdf_path}.pdf', filetype='pdf')
        return True
    except:
        return False
    
def delete_pdf(pdf_path):
    os.remove(f'{pdf_path}.pdf')