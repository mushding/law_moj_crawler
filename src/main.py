from components.order_history import ch_order_to_history
from components.order_pdf import download_reason_pdf
from components.order_reason import pdf_to_reason_json
from components.law_content import LawCrawler

from operations.operations import operations

if __name__ == '__main__':
    # part1 handle order
    # json_file_path = 'data/ChOrder.json'
    # ch_order_to_history(json_file_path)
    # download_reason_pdf(json_file_path)
    # pdf_to_reason_json(json_file_path)

    # part2 handle law
    # law_crawler = LawCrawler()
    # law_crawler.get_law_content_by_crawler()

    # part3 law operations
    operations()