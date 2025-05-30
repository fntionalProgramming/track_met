from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
import pandas as pd

from scrapers.runner_class import Team, Runner

class TrackieScraper:
    def __init__(self, school_name="EHC"):
        self.school_name = school_name

        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Enable headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(service=Service(), options=chrome_options)
        self.team = Team(school_name)
        self.base_url = "https://www.trackie.com"

    def search_events(self, keyword="sssad"):
        """Search Trackie for events using a keyword."""
        self.driver.get(f"{self.base_url}/calendar/")
        search_box = self.driver.find_element(By.ID, "filter_by_title")
        calendar_table = self.driver.find_element(By.ID, "calendar_list")

        old_rows = calendar_table.find_elements(By.TAG_NAME, "tr")
        old_onclicks = [row.get_attribute("onclick") for row in old_rows]

        search_box.clear()
        search_box.send_keys(keyword)

        def table_updated(driver):
            new_rows = driver.find_element(By.ID, "calendar_list").find_elements(
                By.TAG_NAME, "tr"
            )
            new_onclicks = [row.get_attribute("onclick") for row in new_rows]
            return new_onclicks != old_onclicks

        WebDriverWait(self.driver, 10).until(table_updated)

    def extract_event_links(self):
        """Extract event page links from the search results."""
        table = self.driver.find_element(By.ID, "calendar_list")
        links = []
        for row in table.find_elements(By.TAG_NAME, "tr"):
            onclick = row.get_attribute("onclick")
            links.append(
                f"{self.base_url}{onclick.strip("location.href='").strip("';")}"
            )
        return links

    def parse_event_page(self, event_url):
        """Process an individual event page to get Evan Hardy runners."""
        event_name = " ".join(event_url[30:-1].split("/")[0].split("-"))
        self.driver.get(event_url)

        try:
            registrants = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(text(), 'Total Registrants')]")
                )
            )
        except TimeoutException:
            print(f"Failed to load event page: {event_url}")
            return

        if int(registrants.text.split("-")[1].strip().split()[0]) == 0:
            return

        # Go to entry list
        entry_list_url = event_url.replace("event", "entry-list")
        self.driver.get(entry_list_url)
        self.driver.refresh()

        for selector in [".entries_list", ".entries_list.floatRight"]:
            self.process_entries_table(selector, event_name)

    def process_entries_table(
        self,
        selector,
        event_name,
        run_block="force_full_mobile",
        entry_list_class=".entry_list_table_id.sortable.individual_event",
        runner_row_tr="tr_row_inner",
    ):
        """Extract runner info from the entry list table."""
        entry_section = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )

        run_blocks = entry_section.find_elements(By.CLASS_NAME, run_block)
        for block in run_blocks:
            race_name = block.find_element(By.TAG_NAME, "h4").text.split(" - ")[0]
            runners = block.find_element(
                By.CSS_SELECTOR, entry_list_class
            ).find_elements(By.CLASS_NAME, runner_row_tr)

            for runner_row in runners:
                self.extract_runner_info(runner_row, race_name, event_name)

    def extract_runner_info(self, row, race_name, event_name):
        """Extract and store runner info if from Evan Hardy."""
        uid = row.get_attribute("id").split("_")[-1]
        name = row.find_element(By.ID, f"td_2_{uid}").text
        category = row.find_element(By.ID, f"td_3_{uid}").text
        team = (
            row.find_element(By.ID, f"td_4_{uid}")
            .find_element(By.CSS_SELECTOR, "[data-tooltip]")
            .text
        )
        seed = row.find_element(By.ID, f"seed_time_display_{uid}").text
        if team != self.school_name:
            return
        if not self.team.has_runner(name):
            runner = Runner(name, seed, category, team)
            runner.add_race(event_name, race_name)
            self.team.add_runner(runner)
        else:
            self.team.get_runner(name).add_race(event_name, race_name)

    def run_scraper(self, keyword="sssad"):
        self.search_events(keyword)
        links = self.extract_event_links()
        for link in links:
            self.parse_event_page(link)
        self.driver.quit()
        return self.team
    
    def export_team_to_csv(self, filename="Evan Hardy runners.csv"):
        rows = []
        for runner in self.team.runners.values():
            for meet, events in runner.races.items():
                for event in events:
                    rows.append({
                        "Name": runner.name,
                        "Category": runner.category,
                        "Team": runner.team,
                        "Seed Mark": runner.seed_mark,
                        "Meet": meet,
                        "Event": event
                    })
        df = pd.DataFrame(rows)
        df.to_csv(f"storage/{filename}", index=False)
        print(f"csv saved to storage/{filename}")


