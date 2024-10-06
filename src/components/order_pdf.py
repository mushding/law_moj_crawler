from pathlib import Path
from rich.progress import track

from utils.pdf import get_pdf_content, extract_reason_links, is_pdf, delete_pdf
from utils.util import fetch_html, read_json, extract_pcode, convert_update_date, write_pdf, write_odt, write_json


def download_reason_pdf(json_file_path):
    # global variables
    fqdn = 'https://law.moj.gov.tw'
    abnormals = {
        'No Date': [],
        'Not PDF': [],
        'Others': []
    }

    # 1. read json file
    data = read_json(json_file_path)
    update_date = convert_update_date(data.get('UpdateDate', ''))
    
    error_folder = Path('data/order') / update_date / 'error'
    pdf_folder = Path('data/order') / update_date / 'pdf'
    pdf_folder.mkdir(parents=True, exist_ok=True)

    laws = data.get('Laws', [])
    print(f'Found {len(laws)} laws.')

    # loop through all laws
    for law in track(laws):
        # 2. extract pcode
        pcode = extract_pcode(law)        
        url = f'{fqdn}/LawClass/LawHistory.aspx?pcode={pcode}'

        # 3. fetch LawHistory page content
        print(f'Fetching {pcode} url ...')
        html_content = fetch_html(url)

        # 4. extract reason href links
        reason_links, dates = extract_reason_links(html_content, pcode, abnormals)
        if not reason_links:
            print('No reason links found.\n')
            continue

        # loop through all reason links
        for reason_link, date in zip(reason_links, dates):
            try:
                print(f'Processing date of dates: {date} / {dates}')
                reason_url = f'{fqdn}{reason_link}'

                # 5. fetch reason page content, and save to pdf file
                reason_html_content = get_pdf_content(reason_url)
                write_pdf(pdf_folder / pcode, date, reason_html_content)
                print(f"Download {pcode} / {date} pdf, Success")
                if not is_pdf(pdf_folder / pcode / date):
                    abnormals['Not PDF'].append({
                        'Pcode': pcode,
                        'Date': date,
                    })
                    delete_pdf(pdf_folder / pcode / date)
                    print(f"Delete {pcode} / {date} pdf, Success")
                    write_odt(pdf_folder / pcode, date, reason_html_content)
                    print(f"Rewrite {pcode} / {date} to odt, Success\n")
            except Exception as e:
                print(f'Processing {pcode} / {date} failed: {e}')
                abnormals['Others'].append({
                    'Pcode': pcode,
                    'Date': date,
                    'Error': str(e)
                })
        

    write_json(error_folder / 'error_pdf', abnormals)
    print(f'{len(abnormals) / len(laws)} abnormal PDFs found.')
    print(f'{len(abnormals['No Date']) / len(abnormals)} no Date.\n')
    print(f'{len(abnormals["Not PDF"]) / len(abnormals)} not PDFs.')
    print('Finish downloading reason PDFs.\n')

