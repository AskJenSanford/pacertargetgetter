import csv
import time
import scrapy
import requests
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By


case_number_urls = list()


class PacerScraper:
    def __init__(self):
        self.driver = None
        self.request_session = requests.Session()
        self.session_cookies = None

    def login(self):
        self.driver.get("https://pacer.login.uscourts.gov/csologin/login.jsf?appurl=https://pcl.uscourts.gov/pcl/loginCompletion")
        # self.driver.find_element(By.ID, "j_idt140").click()
        time.sleep(2)
        self.driver.find_element(By.ID, "loginForm:loginName").send_keys("hersanford")
        self.driver.find_element(By.ID, "loginForm:password").send_keys("tybdi3-tijsEp-tukmot")
        self.driver.find_element(By.ID, "loginForm:fbtnLogin").click()
        time.sleep(2)

        self.driver.find_element(By.ID, "regmsg:chkRedact").click()
        time.sleep(2)

        self.driver.find_element(By.ID, "regmsg:bpmConfirm").click()

    def case_search(self, case_number=''):
        self.driver.find_element(By.ID, "frmSearch:txtCaseNumber").send_keys(case_number)
        self.driver.find_element(By.ID, "frmSearch:btnSearch").click()

    def parse_case(self, case_number="", page_source=''):
        selector = scrapy.Selector(text=page_source)
        for url in selector.css(
                'tbody[id="frmSearch:caseTable_data"] > tr > td:nth-child(7) > a.ui-link::attr(href)').getall():

            if url:
                case_number_urls.append(url)

        return case_number_urls

    def start_driver(self, case_number):
        self.driver = Chrome()
        self.login()
        time.sleep(2)
        self.driver.find_element(By.ID, "frmSearch:findCasesAdvanced").click()
        self.case_search(case_number=case_number)

        time.sleep(3)
        webdriver_cookies = self.driver.get_cookies()
        for cookie in webdriver_cookies:
            self.request_session.cookies.set(cookie['name'], cookie['value'])

        page_source = self.driver.page_source
        self.driver.quit()
        case_numbers = self.parse_case(case_number=case_number, page_source=page_source)
        return case_numbers
