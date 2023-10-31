import time
import scrapy
import requests
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By

case_number_urls = list()


class PacerScraper:
    def __init__(self):
        self.driver = None
        self.request_session = requests.Session()
        self.session_cookies = None
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless=new')
        self.options.add_argument("start-maximized")
        self.options.add_argument("disable-infobars")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--no-sandbox")

    def login(self):
        try:
            self.driver.get(
                "https://pacer.login.uscourts.gov/csologin/login.jsf?appurl=https://pcl.uscourts.gov/pcl/loginCompletion")
            time.sleep(2)
            self.driver.find_element(By.ID, "loginForm:loginName").send_keys("hersanford")
            self.driver.find_element(By.ID, "loginForm:password").send_keys("tybdi3-tijsEp-tukmot")
            self.driver.find_element(By.ID, "loginForm:fbtnLogin").click()
            time.sleep(2)

            self.driver.find_element(By.ID, "regmsg:chkRedact").click()
            time.sleep(2)

            self.driver.find_element(By.ID, "regmsg:bpmConfirm").click()
        except Exception as e:
            raise Exception(f"An error occurred during login: {str(e)}")

    def case_search(self, case_number=''):
        try:
            self.driver.find_element(By.ID, "frmSearch:txtCaseNumber").send_keys(case_number)
            self.driver.find_element(By.ID, "frmSearch:btnSearch").click()
        except Exception as e:
            raise Exception(f"An error occurred during case search: {str(e)}")

    def parse_case(self, case_number="", page_source=''):
        try:
            selector = scrapy.Selector(text=page_source)
            for url in selector.css(
                    'tbody[id="frmSearch:caseTable_data"] > tr > td:nth-child(7) > a.ui-link::attr(href)').getall():

                if url:
                    case_number_urls.append(url)
        except Exception as e:
            raise Exception(f"An error occurred while parsing the case: {str(e)}")

        return case_number_urls

    def start_driver(self, case_number):
        try:
            self.driver = Chrome(options=self.options)

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
        except Exception as e:
            raise Exception(f"An error occurred during the scraping process: {str(e)}")
