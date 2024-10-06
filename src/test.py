import json
from pathlib import Path
from utils.reason import get_order_reason
from utils.util import write_json

reason_path = Path("./data/20200204.pdf")

reason_json = get_order_reason(reason_path, "", "", {"Two Columns": [], "Scanned PDF": [], "Not PDF": [], "Appendix": [], "Others": []})

print(json.dumps(reason_json, ensure_ascii=False, indent=4))
write_json(Path("./data"), "reason", reason_json)


def _get_law_reason_link(driver, is_abandon):
    law_json = {'LawLevel': '法律'}
    law_name = driver.find_element(By.XPATH, '/html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[3]/table/tbody/tr[3]/td/table/tbody/tr/td').text
    law_modified_date = get_last_modified_date(driver.find_element(By.XPATH, '//*[@id="C_box"]/table/tbody/tr[1]/td').text)
    law_json['LawName'] = law_name
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
        print("沒有修法原因按鈕，換下一個")
        return

    # 等待下一頁加載完成
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    all_windows = driver.window_handles

    # 找到新打開的窗口句柄
    new_window = [window for window in all_windows if window not in original_windows][0]
    driver.switch_to.window(new_window)

    reasons = _get_law_reason(driver)
    law_json['LawReasons'] = reasons

    law_path = Path('data/law') / get_today() / 'reason'
    law_path.mkdir(parents=True, exist_ok=True)
    write_json(law_path / law_name, law_modified_date, law_json)

    driver.close()
    driver.switch_to.window(all_windows[1])
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )