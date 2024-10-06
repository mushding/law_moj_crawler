import os
from rich.progress import track

from utils.util import write_json, read_json, convert_update_date
from utils.reason import get_order_reason
from pathlib import Path


def pdf_to_reason_json(json_file_path):
    error_pcodes = {
        'Two Columns': [],
        'Scanned PDF': [],
        'Not PDF': [],
        'Has Appendix': [],
        'Others': []
    }

    data = read_json(json_file_path)
    update_date = convert_update_date(data.get('UpdateDate', ''))

    error_folder = Path('data/order') / update_date / 'error'
    reason_folder = Path('data/order') / update_date / 'reason'
    reason_folder.mkdir(parents=True, exist_ok=True)
    pdf_folder = Path('data/order') / update_date / 'pdf'

    # os list all files in pdf folder
    for pcode in track(os.listdir(pdf_folder)):
        if 'abnormal' in pcode:
            continue
        print(f'Processing {pcode}...')
        for date in os.listdir(pdf_folder / pcode):
            if not date.endswith('.pdf'):
                continue
            try:
                reason_json = get_order_reason(pdf_folder, pcode, date, error_pcodes)
                date = date.replace('.pdf', '')

                write_json(reason_folder / pcode, date, {
                    'LawId': f'{pcode}_{date}',
                    'LawModifiedDate': date,
                    'LawReasons': reason_json
                })
                print(f'Save order w/ reason of: {pcode} / {date}, Success !\n')
            except Exception as e:
                print(f'Processing {pcode} / {date} failed: {e}')
                error_pcodes['Others'].append({
                    'Pcode': pcode,
                    'Date': date,
                    'Error': str(e)
                })
    write_json(error_folder, 'error_reason', error_pcodes)
    print(f'{len(error_pcodes) / len(os.listdir(pdf_folder))} abnormal PDFs found.')
