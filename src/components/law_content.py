from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pathlib import Path
from rich.progress import Progress
import re
import time
import random

from utils.law import get_last_modified_date, get_today, split_no_and_content
from utils.util import write_json


class LawCrawler:
    def __init__(self):
        self.last_error_page = 1
        self.current_page = 1
        self.pass_first = False
        self.pass_second = False
        self.pass_third = False
        self.pass_forth = False

    def _get_law_content(self, driver, law_name, is_abandon):
        law_json = {'LawLevel': '法律'}
        law_name_local = driver.find_element(By.XPATH, '/html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[3]/table/tbody/tr[3]/td/table/tbody/tr/td').text
        law_modified_date = get_last_modified_date(driver.find_element(By.XPATH, '//*[@id="C_box"]/table/tbody/tr[1]/td').text)
        law_json['LawName'] = law_name_local
        law_json['LawModifiedDate'] = law_modified_date
        law_json['LawURL'] = driver.current_url
        if is_abandon:
            law_json['LawAbandonNote'] = '廢'

        articles = []

        table = driver.find_element(By.XPATH, '//*[@id="C_box"]/table/tbody/tr[2]/td/table')
        contents = table.find_elements(By.XPATH, './tbody/tr')

        for content in contents:
            try:
                # could be 編篇章
                blue_text = content.find_element(By.XPATH, './/font[@color="0000FF"]').text
                blue_text = blue_text.replace(' ', '')
            except:
                blue_text = None

            try:
                # could be 章節款目
                teal_text_list = content.find_elements(By.XPATH, './/font[@color="#3e68ab"]')
            except:
                teal_text_list = None

            try:
                article_no = content.find_element(By.XPATH, './/font[@color="C000FF"]').text
                article_no = article_no.replace(' ', '')
            except:
                article_no = None

            article_content = content.find_element(By.XPATH, './/td[contains(@id, "part")]/table/tbody/tr/td[2]').text
            article_content = article_content.replace(' ', '')

            if blue_text:
                no, content = split_no_and_content(blue_text)
                articles.append({
                    'ArticleType': 'X',  # To be determined later at operation
                    'ArticleNo': no,
                    'ArticleContent': content
                })

            if teal_text_list:
                for teal_text in teal_text_list:
                    teal_texts = teal_text.text
                    for teal_text in teal_texts.split('\n'):
                        teal_text = teal_text.replace(' ', '')
                        no, content = split_no_and_content(teal_text)
                        articles.append({
                            'ArticleType': 'X',
                            'ArticleNo': no,
                            'ArticleContent': content
                        })

            if not article_no:
                law_json['LawForeword'] = article_content
                continue

            articles.append({
                'ArticleType': 'A',
                'ArticleNo': article_no,
                'ArticleContent': article_content
            })

        law_json['LawArticles'] = articles

        law_path = Path('data/law') / get_today() / 'history'
        law_path.mkdir(parents=True, exist_ok=True)
        write_json(law_path / law_name, law_modified_date, law_json)

    def _get_law_reason(self, driver):
        articles = []
        table = driver.find_element(By.XPATH, '/html/body/form/table/tbody/tr[2]/td/table/tbody/tr[2]/td/table')

        article_no_list = table.find_elements(By.XPATH, '//font[@color="#8600B3" and @size="4"]')
        reason_list = table.find_elements(By.XPATH, '//td[@class="artipud_RS_2"]')

        for article_no, reason in zip(article_no_list, reason_list):
            article_no = article_no.text
            reason = reason.text
            articles.append({
                'ArticleType': 'A',
                'Modified': article_no,
                'Current': "",
                'Description': reason
            })
        return articles

    def _get_abandon_reason(self, driver, law_json):
        try:
            abandon_reason_link = driver.find_element(By.XPATH, '//a[img[@src="/lglaw/images/yellow_btn04.png"]]')
            abandon_reason_link.click()
            time.sleep(random.uniform(0, 2))
        except:
            print("[reason abandon] 還沒到廢止的時期，先換下一個")
            return

        # 等待下一頁加載完成
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # 找到新打開的窗口句柄
        all_windows = driver.window_handles
        driver.switch_to.window(all_windows[2])

        print(f'[reason abandon] 正在處理: {law_json["LawName"]} 的廢止原因')
        try:
            reason = driver.find_element(By.XPATH, '/html/body/form/table/tbody/tr[2]/td/table/tbody/tr[2]/td/table/tbody/tr[2]/td[5]').text
        except:
            print("[reason abandon]沒有廢止原因，存入空值")
            reason = ""
        law_json['LawAbandonReason'] = reason

        law_path = Path('data/law') / get_today() / 'reason'
        law_path.mkdir(parents=True, exist_ok=True)
        write_json(law_path / law_json['LawName'], law_json['LawModifiedDate'], law_json)

        driver.close()
        driver.switch_to.window(all_windows[1])
        time.sleep(random.uniform(0, 2))
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

    def _get_law_reason_link(self, driver, law_name, is_abandon):
        law_json = {'LawLevel': '法律'}
        law_name_local = driver.find_element(By.XPATH, '/html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[3]/table/tbody/tr[3]/td/table/tbody/tr/td').text
        law_modified_date = get_last_modified_date(driver.find_element(By.XPATH, '//*[@id="C_box"]/table/tbody/tr[1]/td').text)
        law_json['LawName'] = law_name_local
        law_json['LawModifiedDate'] = law_modified_date
        law_json['LawURL'] = driver.current_url
        if is_abandon:
            law_json['LawAbandonNote'] = '廢'

        # 記錄當前所有窗口句柄
        original_windows = driver.window_handles

        try:
            reason_link = driver.find_element(By.XPATH, '//a[img[@src="/lglaw/images/yellow_btn01.png"]]')
            reason_link.click()
            time.sleep(random.uniform(0, 2))
        except:
            print("[reason] 沒有修法原因按鈕，換下一個")
            if is_abandon:
                self._get_abandon_reason(driver, law_json)
            return

        # 等待下一頁加載完成
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        all_windows = driver.window_handles

        # 找到新打開的窗口句柄
        new_window = [window for window in all_windows if window not in original_windows][0]
        driver.switch_to.window(new_window)

        reasons = self._get_law_reason(driver)
        law_json['LawReasons'] = reasons

        law_path = Path('data/law') / get_today() / 'reason'
        law_path.mkdir(parents=True, exist_ok=True)
        write_json(law_path / law_name, law_modified_date, law_json)

        driver.close()
        driver.switch_to.window(all_windows[1])
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

    def _handle_law_content(self, driver, law_name, is_abandon, is_reason):
        table = driver.find_element(By.XPATH, '//*[@id="TO"]/table/tbody/tr[3]/td/div/table')
        histories = table.find_elements(By.XPATH, './/tr[td/a]')
        for history in histories:
            try:
                history_link = history.find_element(By.TAG_NAME, 'a')
                history_text = history_link.text

                history_link.click()
                time.sleep(random.uniform(0, 2))
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )

                if is_reason:
                    print(f'[reason] 正在處理: {law_name} / {history_text} 的修法原因')
                    self._get_law_reason_link(driver, law_name, is_abandon)
                else:
                    print(f'[history] 正在處理: {law_name} / {history_text} 的法條內容')
                    self._get_law_content(driver, law_name, is_abandon)

                driver.back()
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except Exception as e:
                print(history_link.text, '發生錯誤: ', e)

    def _handle_law_view(self, driver, is_abandon, is_reason):
        table = driver.find_element(By.XPATH, '/html/body/form/table/tbody/tr[2]/td/table/tbody/tr[3]/td/table')
        laws = table.find_elements(By.TAG_NAME, 'tr')[1:]

        original_windows = driver.current_window_handle

        for law in laws:
            link = law.find_element(By.TAG_NAME, 'a')

            law_name = link.text
            print(f"\n[Law] 正在處理: {law_name} 法條")

            link.click()
            WebDriverWait(driver, 10).until(
                EC.number_of_windows_to_be(2)
            )

            all_windows = driver.window_handles

            # 找到新打開的窗口句柄
            new_window = [window for window in all_windows if window not in original_windows][0]
            driver.switch_to.window(new_window)

            # 處理新分頁
            self._handle_law_content(driver, law_name, is_abandon, is_reason)

            driver.close()
            driver.switch_to.window(all_windows[0])
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

    def handle_law_list(self, driver, total_pages, is_abandon=False, is_reason=False):
        with Progress() as progress:
            content_text = "修法原因" if is_reason else "法條內容"
            abandon_text = "廢止法" if is_abandon else "現行法"
            task = progress.add_task(f"[green]處理 {abandon_text} 的 {content_text}...", total=total_pages)

            if is_abandon:
                abandon_link = driver.find_element(By.XPATH, '//*[@id="sub_i"]/ul/li[2]/a')
                abandon_link.click()

            while True:
                print(f"\n==================== 第 {self.current_page} / {total_pages} 頁 ====================")
                time.sleep(random.uniform(0, 2))
                if self.current_page >= self.last_error_page:
                    self._handle_law_view(driver, is_abandon, is_reason)

                self.current_page += 1
                progress.update(task, advance=1)

                try:
                    time.sleep(random.uniform(0, 2))
                    next_button = driver.find_element(By.XPATH, '//input[contains(@title, "最新次頁")]')
                    next_button.click()

                    # 等待下一頁加載完成
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                except:
                    print("沒有下一頁按鈕，結束爬蟲")
                    progress.stop()
                    driver.quit()
                    self.current_page = 1
                    self.last_error_page = 1
                    break

    def get_law_content_by_crawler(self):
        while True:
            try:
                driver = webdriver.Chrome()
                driver.get("https://lis.ly.gov.tw/lglawc/lglawkm")

                category_view = driver.find_element(By.XPATH, '//*[@id="menu02"]')
                category_view.click()

                laws_view = driver.find_element(By.XPATH, '/html/body/form/table/tbody/tr[2]/td/table/tbody/tr[1]/td/ul/li[2]/a')
                laws_view.click()

                # 現行法 的 內容
                if not self.pass_first:
                    self.handle_law_list(driver, total_pages=101)
                self.pass_first = True

                # 廢止法 的 內容
                if not self.pass_second:
                    self.handle_law_list(driver, total_pages=50, is_abandon=True)
                self.pass_second = True

                # 現行法 的 修法原因
                if not self.pass_third:
                    self.handle_law_list(driver, total_pages=101, is_reason=True)
                self.pass_third = True

                # 廢止法 的 修法原因
                if not self.pass_forth:
                    self.handle_law_list(driver, total_pages=50, is_reason=True, is_abandon=True)
                self.pass_forth = True

                driver.quit()
                break
            except Exception as e:
                print(f"第 {self.current_page} 頁發生錯誤，重新嘗試")
                print(e)
                self.last_error_page = self.current_page
                self.current_page = 1
                driver.quit()
                continue
