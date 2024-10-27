import time
import requests
from rich.progress import track
from bs4 import BeautifulSoup
import re
from pathlib import Path
import json
import os

from utils.util import read_json, write_json

def _fetch_html(fqdn, code):
    params = {
        "CODE": code
    }
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Cookie": "ASP.NET_SessionId=53m5byrglvro1rwuqmgo1kfx; showmode=",
        "DNT": "1",
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
    response = requests.get(fqdn, headers=headers, params=params)
    response.encoding = 'utf-8'
    return response.text


def _get_law_name_by_url_idx(fqdn, code):
    html_content = _fetch_html(fqdn, code)
    soup = BeautifulSoup(html_content, 'lxml')
    law_name = soup.find(class_='law_NA').text

    # 國際機場園區發展條例(01070) -> 國際機場園區發展條例
    law_name = re.sub(r'\(\d+\)', '', law_name).strip()
    return law_name


def _is_law_url_valid(fqdn, code):
    html_content = _fetch_html(fqdn, code)
    soup = BeautifulSoup(html_content, 'lxml')
    if soup.find('title', string="立法院法律系統"):
        return True
    return False


def _gen_law_url_map():
    for idx in track(range(10000, 100000)):
        fqdn = 'https://www.ly.gov.tw/Pages/ashx/LawRedirect.ashx'
        code = f'{idx:05d}'
        print(f'Checking code: {code}')
        while True:
            try: 
                if _is_law_url_valid(fqdn, code):
                    law_name = _get_law_name_by_url_idx(fqdn, code)
                    print(f'Found law: {code} -> {law_name}')

                    # Save to law_name_url_map.json
                    law_name_url_map_path = Path('data/operation/law_name_url_map.json')
                    law_name_url_map = read_json(law_name_url_map_path)
                    law_name_url_map[law_name] = f'https://www.ly.gov.tw/Pages/ashx/LawRedirect.ashx?CODE={code}'
                    json.dump(law_name_url_map, Path('data/operation/law_name_url_map.json').open('w'), ensure_ascii=False, indent=4)
                break
            except:
                print(f'Internet Error: {code}, retrying after 60s...')
                time.sleep(60)

def add_law_link_to_law_history(law_operation_history_folder):
    # _gen_law_url_map()
    law_name_url_map_path = Path('data/operation/law_name_url_map.json')
    law_name_pcode_map_path = Path('data/operation/law_name_pcode_map.json')
    law_name_url_map = read_json(law_name_url_map_path)
    law_name_pcode_map = read_json(law_name_pcode_map_path)
    pcode_law_name_map = {v: k for k, v in law_name_pcode_map.items()}

    law_codes = os.listdir(law_operation_history_folder)
    for law_code in track(law_codes, description='[bold red]Adding law link to law history...'):
        law_name = pcode_law_name_map[law_code]
        for modified_date in os.listdir(law_operation_history_folder / law_code):
            law = read_json(law_operation_history_folder / law_code / modified_date)
            try:
                law['LawURL'] = law_name_url_map[law_name]
            except KeyError:
                # print(f'No law link found for {law_name} / {modified_date}, skipping...')
                continue
            write_json(law_operation_history_folder / law_code, modified_date.split('.')[0], law)
            # print(f'Add law link to {law_code} / {modified_date}, Success !')