import os
from rich.progress import track
from pathlib import Path

from utils.util import read_json, write_json, extract_pcode


def _gen_pcode_not_found_in_ch_law(custom_pcode):
    return f'Z{custom_pcode:07d}'


def _gen_law_name_pcode_map(ch_law_json):
    ch_law = read_json(ch_law_json)
    law_name_ch_law_lisly_map = read_json(Path('data/operation/law_name_ch_law_lisly_map.json'))
    law_name_pcode_map = {}

    laws = ch_law.get('Laws', [])

    for law in laws:
        pcode = extract_pcode(law)
        law_name = law.get('LawName', '')
        
        # map some law name from 全國法規資料庫 to 立法院法律系統
        if law_name in law_name_ch_law_lisly_map:
            law_name = law_name_ch_law_lisly_map[law_name]

        law_name_pcode_map[law_name] = pcode

    return law_name_pcode_map


def add_pcode_to_law_history(ch_law_json, law_history_folder, law_operation_history_folder):
    custom_pcode = 1
    law_name_pcode_map = _gen_law_name_pcode_map(ch_law_json)

    law_names = os.listdir(law_history_folder)
    for law_name in track(law_names, description='[bold red]Adding pcode to law history...'):
        try:
            pcode = law_name_pcode_map[law_name]
        except KeyError:
            # print(f'No pcode found for {law_name}, generating custom pcode...')
            pcode = _gen_pcode_not_found_in_ch_law(custom_pcode)
            law_name_pcode_map[law_name] = pcode
            custom_pcode += 1

        modified_dates = os.listdir(law_history_folder / law_name)
        for modified_date in modified_dates:
            law = read_json(law_history_folder / law_name / modified_date)
            law['LawPcode'] = pcode
            write_json(law_operation_history_folder / pcode, modified_date.split('.')[0], law)
    write_json(Path('data/operation'), 'law_name_pcode_map', law_name_pcode_map)
