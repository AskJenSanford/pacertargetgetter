import time
import scrapy
import pandas as pd
from urllib.parse import urljoin
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": 'D:\pacer',
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True
})

driver = Chrome(options=chrome_options)


def login():
    driver.get("https://pcl.uscourts.gov/pcl/index.jsf")

    driver.find_element(By.ID, "loginForm:loginName").send_keys("hersanford")
    driver.find_element(By.ID, "loginForm:password").send_keys("tybdi3-tijsEp-tukmot")
    driver.find_element(By.ID, "loginForm:fbtnLogin").click()
    time.sleep(2)

    driver.find_element(By.ID, "regmsg:chkRedact").click()
    time.sleep(2)

    driver.find_element(By.ID, "regmsg:bpmConfirm").click()


df = pd.read_csv('case_file.csv')
urls = set(df.url)
try:
    login()
    time.sleep(5)

    for url in urls:
        driver.get(url)
        driver.find_element(By.PARTIAL_LINK_TEXT, "History/Documents.").click()
        driver.find_element(By.NAME, "button1").click()
        page_source = driver.page_source
        pdf_selector = scrapy.Selector(text=page_source)
        for tr in pdf_selector.css('table > tbody > tr[valign="top"]'):
            desc = ''.join(tr.css("td:last-child ::text").getall()).lower()
            if "affidavit of service" in desc:
                pdf_page_url = tr.css("td:nth-child(1) > a::attr(href)").get()
                if pdf_page_url:
                    pdf_file_url = urljoin("https://ecf.cand.uscourts.gov/", pdf_page_url)
                    driver.get(pdf_file_url)
                    driver.find_element(By.PARTIAL_LINK_TEXT, "Continue").click()
                    driver.find_element(By.CSS_SELECTOR, 'input[value="View Document"]').click()
                    time.sleep(3)
                    # driver.find_element(By.TAG_NAME, "body").send_keys(Keys.CONTROL + 's')
                    # driver.find_element(By.NAME, 'Save').send_keys(Keys.ENTER)
                    # driver.execute_script("window.print();")

    time.sleep(10)
    driver.quit()

except Exception as e:
    print(e)
    driver.quit()
