from datetime import datetime
import re


def get_last_modified_date(text):
    # 提取年份、月份和日期
    parts = text.split('年')
    year = int(parts[0].replace('中華民國', '').strip()) + 1911
    month_day = parts[1].split('月')
    month = int(month_day[0].strip())
    day = int(month_day[1].replace('日', '').strip())

    # 格式化為西元日期字串
    western_date = f"{year:04d}{month:02d}{day:02d}"
    return western_date


def get_today():
    today = datetime.today()

    # 格式化為 YYYYMMDD 字串
    return today.strftime('%Y%m%d')


def split_no_and_content(text):
    # 用正則表達式匹配章節號和章節內容
    match = re.match(r'(.*第[一二三四五六七八九十百千]+[編章類節款目條])(.+)$', text)
    if match:
        return match.group(1), match.group(2)
    return None, None
