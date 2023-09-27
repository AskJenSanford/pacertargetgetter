import time
import scrapy
import requests
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from urllib.parse import urljoin

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


def case_search():
    driver.find_element(By.ID, "frmSearch:txtCaseNumber").send_keys("3:2022cv02570")
    driver.find_element(By.ID, "frmSearch:btnSearch").click()


def parse_case(page_source):
    selector = scrapy.Selector(text=page_source)
    for url in selector.css(
            'tbody[id="frmSearch:caseTable_data"] > tr > td:nth-child(7) > a.ui-link::attr(href)').getall():
        hist_response = request_session.get(url)
        hist_selector = scrapy.Selector(text=hist_response.text)
        hist_url = hist_selector.css("a:contains('History/Documents...')::attr(href)").get()
        if hist_url:
            joinurl = urljoin("https://ecf.cand.uscourts.gov/", hist_url)
            query_response = request_session.get(joinurl)
            query_selector = scrapy.Selector(text=query_response.text)
            detail_page_url = query_selector.css('form[method="POST"]::attr(action)').get()
            detail_page_url = urljoin("https://ecf.cand.uscourts.gov/", detail_page_url)
            time.sleep(1)

            pdf_page = request_session.post(url=detail_page_url, data=payload)
            pdf_selector = scrapy.Selector(text=pdf_page.text)
            for tr in pdf_selector.css('table > tr[valign="top"]'):
                desc = ''.join(tr.css("td:last-child ::text").getall()).lower()
                if "affidavit of service" in desc:
                    pdf_page_url = tr.css("td:nth-child(1) > a::attr(href)").get()
                    if pdf_page_url:
                        pdf_file_url = urljoin("https://ecf.cand.uscourts.gov/", pdf_page_url)

                        pdf_content = request_session.post(pdf_file_url, data=pdf_payload)
                        with open("file.pdf", mode="wb") as file:
                            file.write(pdf_content.content)
                            print("done")


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
parse_case(page_source)
