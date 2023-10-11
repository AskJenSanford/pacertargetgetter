import csv
import time
import scrapy
import requests
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By

file = open("case_file.csv", mode='a', newline='')
file = csv.writer(file)
file.writerow(['case_number', 'url'])

try:
    driver = Chrome()
    request_session = requests.Session()
    session_cookies = None
    payload = {'QueryType': 'History', 'sort1': 'asc'}
    pdf_payload = {'caseid': '369930',
                   'de_seq_num': '19',
                   'got_receipt': '1',
                   'pdf_toggle_possible': '1'}


    def login():
        driver.get("https://pcl.uscourts.gov/pcl/index.jsf")

        driver.find_element(By.ID, "loginForm:loginName").send_keys("hersanford")
        driver.find_element(By.ID, "loginForm:password").send_keys("tybdi3-tijsEp-tukmot")
        driver.find_element(By.ID, "loginForm:fbtnLogin").click()
        time.sleep(2)

        driver.find_element(By.ID, "regmsg:chkRedact").click()
        time.sleep(2)

        driver.find_element(By.ID, "regmsg:bpmConfirm").click()


    def case_search(case_number="3:2022cv02570"):
        driver.find_element(By.ID, "frmSearch:txtCaseNumber").send_keys(case_number)
        driver.find_element(By.ID, "frmSearch:btnSearch").click()


    def parse_case(case_number="3:2022cv02570", page_source=''):
        selector = scrapy.Selector(text=page_source)
        for url in selector.css(
                'tbody[id="frmSearch:caseTable_data"] > tr > td:nth-child(7) > a.ui-link::attr(href)').getall():

            if url:
                file.writerow([case_number, url])
                print("save")


    login()
    time.sleep(2)
    driver.find_element(By.ID, "frmSearch:findCasesAdvanced").click()
    case_search()

    time.sleep(3)
    webdriver_cookies = driver.get_cookies()
    for cookie in webdriver_cookies:
        request_session.cookies.set(cookie['name'], cookie['value'])

    page_source = driver.page_source
    driver.quit()
    parse_case(page_source=page_source)

except Exception as e:
    print(e)
    driver.quit()
