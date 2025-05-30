from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import pandas as pd
from selenium.webdriver.chrome.options import Options

class ScraperSSSAD:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(service=Service(), options=chrome_options)
        self.base_url = "https://docs.google.com/spreadsheets/d/1kF5uW-spG6SA5HpLb3TQ3gzhJjgO6-39/edit?gid=193232266#gid=193232266"
    def go_to_csv_page(self):
        pass # too lazy to implment rn
    def run_scrapper(self):
        # download the csv that wil be collected 
        self.driver.get(self.base_url)
        meets_tab = self.driver.find_element(By.CSS_SELECTOR, "div.docs-sheet-container-bar.goog-toolbar.goog-inline-block")
        meet_names = meets_tab.text.split("\n")[:-1]
        meets = meets_tab.find_elements(By.XPATH, "./div")
        for i, meet in enumerate(meets):
            meet.click()
            current_url = self.driver.current_url
            download_url = current_url[:current_url.rfind("/") + 1] + f"export?format=xlsx&{current_url[current_url.find("#gid="):]}".replace("#", "")
            df = pd.read_excel(download_url)
            if df.iloc[:, 0].isna().all():
                df = df.iloc[:, 1:]
            meet_name = meet_names[i]
            if meet_name[0] == " ":
                meet_name = meet_name[1:]
            df.to_html(f"storage/{meet_name}.html", index=False)
    