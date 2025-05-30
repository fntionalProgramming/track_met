from scrapers.sssad_scraper import ScraperSSSAD
from scrapers.trackie_scraper import TrackieScraper
from analyze_meet import GenerateAthleteSchedule



if __name__ == "__main__":
    scraper = TrackieScraper()
    evan_hardy_team = scraper.run_scraper()
    scraper.export_team_to_csv()

    

    scrapper_sssad = ScraperSSSAD()
    scrapper_sssad.run_scrapper()

    s = GenerateAthleteSchedule()
    s.run()