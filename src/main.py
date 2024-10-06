from pathlib import Path
import signal
import sys

from components.order_history import ch_order_to_history
from components.order_pdf import download_reason_pdf
from components.order_reason import pdf_to_reason_json
from components.law_content import LawCrawler


def signal_handler(sig, frame):
    print('接收到 Ctrl+C，結束程式')
    sys.exit(0)



if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    
    json_file_path = 'data/ChOrder.json'
    # ch_order_to_history(json_file_path)
    # download_reason_pdf(json_file_path)
    # pdf_to_reason_json(json_file_path)

    law_crawler = LawCrawler()
    law_crawler.get_law_content_by_crawler()
