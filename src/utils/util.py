import json
import re
import requests
from datetime import datetime


def fetch_html(url):
    # Random sleep to mimic user behavior
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
    response = requests.get(url)
    return response.text


def read_json(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8-sig') as file:
        data = json.load(file)
    return data


def write_json(json_file_path, file_name, data):
    json_file_path.mkdir(parents=True, exist_ok=True)
    with open(f'{json_file_path / file_name}.json', 'w', encoding='utf-8-sig') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def write_pdf(pdf_file_path, file_name, data):
    pdf_file_path.mkdir(parents=True, exist_ok=True)
    with open(f'{pdf_file_path / file_name}.pdf', 'wb') as file:
        file.write(data)

def write_odt(odt_file_path, file_name, data):
    odt_file_path.mkdir(parents=True, exist_ok=True)
    with open(f'{odt_file_path / file_name}.odt', 'wb') as file:
        file.write(data)


def convert_update_date(update_date):
    update_date = update_date.replace('上午', 'AM').replace('下午', 'PM')
    date_obj = datetime.strptime(update_date, '%Y/%m/%d %p %I:%M:%S')
    formatted_date = date_obj.strftime('%Y%m%d')

    return formatted_date


def extract_pcode(law):
    law_url = law.get('LawURL', '')
    match = re.search(r'pcode=([A-Za-z0-9]+)', law_url)

    return match.group(1)
