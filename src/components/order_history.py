from rich.progress import track
from pathlib import Path
import os

from utils.util import fetch_html, read_json, write_json, convert_update_date, extract_pcode
from utils.history import extract_history_links, parse_law_articles, add_law_id_field, generalize_chapters, add_history_index_field

def ch_order_to_history(json_file_path):
    # global variables
    fqdn = 'https://law.moj.gov.tw'

    # 1. read json file
    data = read_json(json_file_path)
    update_date = convert_update_date(data.get('UpdateDate', ''))
    laws = data.get('Laws', [])
    print(f'Found {len(laws)} laws.')
    
    history_folder = Path('data/order') / update_date / 'history'

    # loop through all laws
    for law in track(laws):
        # 2. extract pcode
        pcode = extract_pcode(law)
        url = f'{fqdn}/LawClass/LawHistory.aspx?pcode={pcode}'

        # 3. fetch LawHistory page content
        print(f'Fetching {pcode} url ...')
        html_content = fetch_html(url)

        # 4. extract history href links
        latestModifiedDate = law.get('LawModifiedDate', "")
        history_links, lnndates = extract_history_links(html_content)

        # save latest order to json file w/ basic info
        if not history_links:
            print('No history links found.')
            law = generalize_chapters(law)
            write_json(history_folder / pcode, latestModifiedDate, add_law_id_field(pcode, latestModifiedDate, law))
            print(f'Save order of: {pcode} / {latestModifiedDate}, Success !\n')
            continue

        # loop through all history links
        for history_link, lnndate in zip(history_links, lnndates):
            print(f'Processing lnndate of lnndates: {lnndate} / {lnndates}')
            history_url = f'{fqdn}{history_link}'

            # 5. fetch history page content
            history_html_content = fetch_html(history_url)

            # 6. parse law articles, and convert to law_moj json format
            law_articles_json = parse_law_articles(history_html_content)

            # 7. save history order to json file w/o basic info
            write_json(history_folder / pcode, lnndate, {
                'LawId': f'{pcode}_{lnndate}',
                'LawModifiedDate': lnndate,
                'LawArticles': law_articles_json
            })
            print(f'Save order w/ history of: {pcode} / {lnndate}, Success !\n')

        # 8. save latest order to json file w/ basic info
        law = generalize_chapters(law)
        write_json(history_folder / pcode, latestModifiedDate, add_law_id_field(pcode, lnndate, law))
        print(f'Save order w/ history of: {pcode} / {latestModifiedDate}_latest, Success !\n')


def order_add_history_field(json_file_path):
    data = read_json(json_file_path)
    update_date = convert_update_date(data.get('UpdateDate', ''))

    history_folder = Path('data/order') / update_date / 'history'
    order_folder = Path('data/order') / update_date / 'order'
    order_folder.mkdir(parents=True, exist_ok=True)
    
    for pcode in track(os.listdir(history_folder)):
        print(f'Processing {pcode} ...')
        dates = os.listdir(history_folder / pcode)
        dates = [history.replace('.json', '') for history in dates]
        dates.sort(reverse=True)

        for idx, date in enumerate(dates):
            print(f'Processing {pcode} / {dates[idx:]} ...')
            date_json = read_json(history_folder / pcode / f'{date}.json')
            date_json = add_history_index_field(date_json, dates[idx:])
            write_json(order_folder / pcode, date, date_json)
