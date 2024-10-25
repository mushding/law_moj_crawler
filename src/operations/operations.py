from pathlib import Path

from operations.utils.pcode import add_pcode_to_law_history
from operations.utils.law_url import add_law_link_to_law_history
from operations.utils.detail_field import add_detail_field
from operations.utils.lisly_additional_field import add_lisly_not_found_to_law_history

def operations():
    law_version = '20241011'
    order_version = '20240913'
    ch_law = 'data/ChLaw.json'
    ch_order = 'data/ChOrder.json'
    law_history_folder = Path(f'data/law/{law_version}/history')
    law_reason_folder = Path(f'data/law/{law_version}/reason')
    order_history_folder = Path(f'data/order/{order_version}/history')
    order_reason_folder = Path(f'data/order/{order_version}/reason')
    law_operation_history_folder = Path(f'data/operation/law/{law_version}/history')
    law_operation_reason_folder = Path(f'data/operation/law/{law_version}/reason')
    order_operation_history_folder = Path(f'data/operation/order/{order_version}/history')
    order_operation_reason_folder = Path(f'data/operation/order/{order_version}/reason')


    # add_pcode_to_law_history(ch_law, law_history_folder, law_operation_history_folder)
    # add_law_link_to_law_history(law_operation_history_folder)
    # add_detail_field(ch_law, law_operation_history_folder)
    add_lisly_not_found_to_law_history(ch_law, law_operation_history_folder)

