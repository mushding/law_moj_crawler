from utils.util import read_json, write_json
from pathlib import Path
from rich.progress import track

def add_lisly_not_found_to_law_history(ch_law, law_operation_history_folder):
    ch_law = read_json(ch_law)
    law_name_pcode_map_path = Path('data/operation/law_name_pcode_map.json')
    law_name_pcode_map = read_json(law_name_pcode_map_path)
    law_name_lisly_not_found_list_path = Path('data/operation/law_name_lisly_not_found_list.json')
    law_name_lisly_not_found_list = read_json(law_name_lisly_not_found_list_path)

    for not_found_name in track(law_name_lisly_not_found_list, description='[bold red]Adding lisly not found to law history...'):
        laws = ch_law.get('Laws', [])
        for law in laws:
            if law.get('LawName', '') == not_found_name:
                pcode = law_name_pcode_map[not_found_name]
                law_history_pcode_folder = law_operation_history_folder / pcode
                modified_date = law.get('LawModifiedDate', '')
                # print(f'Found {not_found_name} ({pcode}) / {modified_date}..., adding to operation folder...')
                write_json(law_history_pcode_folder, modified_date, law)
                break
        