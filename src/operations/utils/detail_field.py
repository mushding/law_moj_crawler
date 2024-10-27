# LawCategory
# LawHasEngVersion
# LawHistories
# LawEffectiveDate
# LawEffectiveNote
# EngLawName
# LawAttachments

from utils.util import read_json, write_json
from pathlib import Path
import os
from rich.progress import track

def add_detail_field(ch_law, law_operation_history_folder):
    ch_law = read_json(ch_law)
    law_name_ch_law_lisly_map = read_json(Path('data/operation/law_name_ch_law_lisly_map.json'))
    law_name_pcode_map = read_json(Path('data/operation/law_name_pcode_map.json'))
    law_name_lisly_not_found_list = []
    laws = ch_law.get('Laws', [])

    for law in track(laws):
        detail_field = {
            "LawCategory": law.get('LawCategory', ""),
            "LawHasEngVersion": law.get('LawHasEngVersion', ""),
            "LawHistories": law.get('LawHistories', ""),
            "LawEffectiveDate": law.get('LawEffectiveDate', ""),
            "LawEffectiveNote": law.get('LawEffectiveNote', ""),
            "EngLawName": law.get('EngLawName', ""),
            "LawAttachments": law.get('LawAttachements', {})
        }
        law_name = law.get('LawName', "")
        # map some law name from 全國法規資料庫 to 立法院法律系統
        if law_name in law_name_ch_law_lisly_map:
            law_name = law_name_ch_law_lisly_map[law_name]

        law_pcode = law_name_pcode_map[law_name]
        law_history_pcode_folder = law_operation_history_folder / law_pcode
        if not os.path.exists(law_history_pcode_folder):
            print(f'{law_name} ({law_pcode}) does not exist in the operation folder.')
            law_name_lisly_not_found_list.append(law_name)
            continue
        
        for modified_date in os.listdir(law_history_pcode_folder):
            # print(f'Processing {law_name} ({law_pcode}) / {modified_date}...')
            modified_date_file = read_json(law_history_pcode_folder / modified_date)
            modified_date_file['LawCategory'] = detail_field['LawCategory']
            modified_date_file['LawHasEngVersion'] = detail_field['LawHasEngVersion']
            modified_date_file['LawHistories'] = detail_field['LawHistories']
            modified_date_file['LawEffectiveDate'] = detail_field['LawEffectiveDate']
            modified_date_file['LawEffectiveNote'] = detail_field['LawEffectiveNote']
            modified_date_file['EngLawName'] = detail_field['EngLawName']
            modified_date_file['LawAttachments'] = detail_field['LawAttachments']
            write_json(law_history_pcode_folder, modified_date.split('.')[0], modified_date_file)
    write_json(Path('data/operation'), 'law_name_lisly_not_found_list', law_name_lisly_not_found_list)
