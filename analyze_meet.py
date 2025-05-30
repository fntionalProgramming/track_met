from bs4 import BeautifulSoup
import pathlib
import re
import pandas as pd


class GenerateAthleteSchedule:
    def __init__(self):
        self.runners_csv = "storage/Evan Hardy runners.csv"
        self.pattern = r"\b(?:[01]?\d|2[0-3]):[0-5]\d:[0-5]\d\b"
        self.pattern_event = r"\(([A-Z]+)\)"
        self.category_map = {
            'I': 'Intermediate', 'S': 'Senior', 'J': 'Junior'
        }
        self.gender_map = {
            'G': 'Female', 'B': 'Male'
        }
        self.event_map = {
            "TJ": "Triple Jump",
            "Discus": "Discus Throw",
            "4 x 100 M": "This registrant is competing on a relay only",
            "100 M": "100m",
            "200 M": "200m",
            "400 M": "400m",
            "800 M": "800m",
            "1500 M": "1500m",
            "3000 M": "3000m",
            "Pole Vault": "Pole Vault",
            "High Jump": "High Jump",
            "Hurdles": "Hurdles",
            "HJ": "High Jump",
            "LJ": "Long Jump",
            "Shot": "Shot Put"
        }
    def generate_directory(self, file_path):
        with open(f"storage/{file_path}", 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'lxml')
        tbody = soup.find('tbody')
        trs = tbody.find_all("tr")
        # the first tr will be the meet name
        # the second tr will be the complex to meet at
        first_row = trs[0].find("td").get_text(strip=True)
        facility = trs[1].find("td").get_text(strip=True)
        spllited_first_row = first_row.split(" - ")
        # generate the directories for each meet
        meet_name = f"{spllited_first_row[0]} {spllited_first_row[1]}".lower()
        meet_directory = pathlib.Path(meet_name)
        meet_directory.mkdir(parents=True, exist_ok=True)

        info_file = pathlib.Path(f"{meet_name[:-1]}/info.txt")
        info_file.parent.mkdir(parents=True, exist_ok=True)
        info_file.write_text(f"Date of meet: {spllited_first_row[2]}\nTime of the meet: {spllited_first_row[-1]}\nLocation of the meet: {facility}")
        # get the informationn such as the officiasl, volunteer and events
        schedule_index = 0
        for i, tr in enumerate(trs):
            if tr.find("td").get_text(strip=True) == "Rolling Schedule - All Times are Approximate":
                schedule_index = i
                break
        # make the info file that display the basic info
        return trs, schedule_index
    def build_athlete_schedule_track(self, file_path, trs, schedule_index):      
        df = pd.read_csv(self.runners_csv)
        # building the vector for track
        i = schedule_index
        query_meet = f"sssad {file_path[:-5].lower()}"
        df = df[df['Meet'] == query_meet]
        df['Time'] = ""
        df['Location'] = ""
        def add_track_timeline(i, df, time):
            tds = trs[i].find_all("td")
            category = tds[1].get_text(strip=True)
            event_type = tds[2].get_text(strip=True)

            query_catergory = self.category_map[category[0]]
            query_gender = self.gender_map[category[1]]
            query_event = f"{query_gender} {self.event_map[event_type]}"
            if self.event_map[event_type] == "Hurdles":
                query_event = "Hurdles"
            if len(df) == 0:
                return df
            for index, row in df.iterrows():
                if row['Category'] == query_catergory and query_event in row['Event']:    
                    df.at[index, 'Time'] = time
                    df.at[index, 'Location'] = "Track"
            return df
        while i < len(trs):
            # starting of a track time
            if len(re.findall(self.pattern, trs[i].find("td").get_text(strip=True))) != 0:
                tds = trs[i].find_all("td")
                time = tds[0].get_text(strip=True)
                filtered_df = add_track_timeline(i, df, time)
                if len(filtered_df) == 0:
                    return
                i += 1
                # while the column is nan it would be the same time
                while i < len(trs) and trs[i].find("td").get_text(strip=True).lower() == "nan":
                    new_filtered_df = add_track_timeline(i, filtered_df, time)
                    filtered_df = new_filtered_df
                    i += 1
                continue
            i += 1
        output_path = f"{file_path[:-5].lower()}/athlete_schedule.csv"
        filtered_df.to_csv(output_path, index=False)
        print(f"Saved updated athlete schedule to {output_path}")
        return filtered_df
    def build_athlete_schedule_field(self, file_path, trs, schedule_index, df):
        # iterate to the first time line
        def cell_is_nan(td):
            return td.get_text(strip=True).lower() == "nan"
        i = schedule_index
        df = pd.read_csv(f"{file_path[:-5].lower()}/athlete_schedule.csv")
        while len(re.findall(self.pattern, trs[i].find_all("td")[3].get_text(strip=True))) == 0:
            i += 1
        filled_category_row = []
        for cell in trs[i - 1].find_all("td")[4:]:
            filled_category_row.append(cell.get_text(strip=True))
        while i < len(trs) and len(re.findall(self.pattern, trs[i].find_all("td")[3].get_text(strip=True))) != 0:
            print(i)
            for j, field_event in enumerate(filled_category_row):
                time = trs[i].find_all("td")[3].get_text(strip=True)
                if not cell_is_nan(trs[i].find_all("td")[j + 4]):
                    categories = trs[i].find_all("td")[j + 4].get_text(strip=True).split("/")
                    # check if ther first two characer is a event or nort
                    query_categories = [categories[0][:2]] if len(categories) == 1 else categories
                    # get the location
                    location = "Field"
                    if field_event[:2] in self.event_map:
                        location += " - " + field_event.split(" - ")[1]
                        field_event = self.event_map[field_event[:2]]
                    elif len(re.findall(self.pattern_event, field_event)) != 0:
                        location += " - " + re.findall(self.pattern_event, field_event)[0]
                        field_event = field_event.split(" ")[0]
                    print(location)
                    for query_category in query_categories:
                        query_gender = self.gender_map[query_category[1]]
                        query_category = self.category_map[query_category[0]]
                        query_event_name = f"{query_gender} {field_event}"
                        for index, rows in df.iterrows():
                            if query_event_name in rows['Event']:
                                df.at[index, 'Location'] = location
                                df.at[index, 'Time'] = time
            i += 1
        output_path = f"{file_path[:-5].lower()}/athlete_schedule.csv"
        df.to_csv(output_path, index=False)
        print(f"Updated field data saved to {output_path}")

    def run(self, dir="storage"):
        directory = pathlib.Path(dir)
        for file in directory.iterdir():
            if file.suffix == ".html":
                schedule, schedule_index = self.generate_directory(file.name)
                df = self.build_athlete_schedule_track(file.name, schedule, schedule_index)
                if df is None:
                    continue
                self.build_athlete_schedule_field(file.name, schedule, schedule_index, df)



