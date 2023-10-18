import os
import time
import scrapy
from urllib.parse import urljoin
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from .pdf_processing import PDFImageProcessor
from selenium.webdriver.chrome.options import Options



class PdfData:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_experimental_option("prefs", {
            "download.default_directory": r"D:/pacer/pacer_scraper/casepdf",
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True
        })
        self.driver = None

    def login(self):
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

    def scrape_pdf_data(self, case_number, case_number_urls):
        try:
            self.driver = Chrome(options=self.chrome_options)
            self.login()
            time.sleep(5)

            # df = pd.read_csv('case_file.csv')
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
                            time.sleep(5)

                            pdfimage = PDFImageProcessor(file_number=pdf_id, case_number=case_number)
                            pdfimage.start_pdf()

            time.sleep(10)
        except Exception as e:
            print(e)
        finally:
            self.driver.quit()
