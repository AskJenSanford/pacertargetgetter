import os
import time
import scrapy
from ..models import Address
from django.conf import settings
from urllib.parse import urljoin
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from .pdf_processing import PDFImageProcessor
from selenium.webdriver.chrome.options import Options

pdf_directory = os.path.join(settings.BASE_DIR, "casepdf")


class PdfData:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_experimental_option("prefs", {
            "download.default_directory": pdf_directory,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True
        })

        self.chrome_options.add_argument('--headless=new')
        self.chrome_options.add_argument("start-maximized")
        self.chrome_options.add_argument("disable-infobars")
        self.chrome_options.add_argument("--disable-extensions")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--no-sandbox")
        self.driver = None
        self.addresses = list()

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
            raise Exception(f"An error occurred while parsing the case: {str(e)}")

    def scrape_pdf_data(self, case_number, case_number_urls):
        try:
            self.driver = Chrome(options=self.chrome_options)
            self.login()
            time.sleep(5)

            urls = set(case_number_urls)

            for url in urls:
                self.driver.get(url)
                self.driver.find_element(By.PARTIAL_LINK_TEXT, "History/Documents.").click()
                self.driver.find_element(By.NAME, "button1").click()
                page_source = self.driver.page_source
                pdf_selector = scrapy.Selector(text=page_source)

                for tr in pdf_selector.css('table > tbody > tr[valign="top"]'):
                    desc = ''.join(tr.css("td:last-child ::text").getall()).lower()
                    if "affidavit of service" in desc:
                        pdf_page_url = tr.css("td:nth-child(1) > a::attr(href)").get()
                        if pdf_page_url:
                            pdf_id = pdf_page_url.split('/')[-1]
                            pdf_file_url = urljoin("https://ecf.cand.uscourts.gov/", pdf_page_url)
                            self.driver.get(pdf_file_url)
                            self.driver.find_element(By.PARTIAL_LINK_TEXT, "Continue").click()
                            self.driver.find_element(By.CSS_SELECTOR, 'input[value="View Document"]').click()
                            max_wait_time = 100

                            check_interval = 15

                            start_time = time.time()
                            file_path = os.path.join(pdf_directory, f"{pdf_id}.pdf")
                            while not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
                                if time.time() - start_time > max_wait_time:
                                    break
                                time.sleep(check_interval)

                            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                                pdfimage = PDFImageProcessor(file_number=pdf_id)
                                address_list = pdfimage.start_pdf()
                                self.addresses.extend(address_list)

            self.driver.quit()
            Address(case_number=case_number, address=self.addresses).save()
            print(f"Insert address of {case_number}.")

        except Exception as e:
            raise Exception(f"An error occurred while scraping PDF data: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()
