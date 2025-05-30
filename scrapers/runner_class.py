class Runner:
    def __init__(self, name, seed_mark, category, team):
        self.name = name
        self.seed_mark = seed_mark
        self.category = category
        self.team = team
        self.races = {}

    def add_race(self, meet_name, event_name):
        if meet_name not in self.races:
            self.races[meet_name] = []
        if event_name not in self.races[meet_name]:
            self.races[meet_name].append(event_name)

    def get_schedule(self):
        return {
            "Name": self.name,
            "Category": self.category,
            "Team": self.team,
            "Seed Mark": self.seed_mark,
            "Events": self.races,
        }

    def show_info(self):
        print(f"Name: {self.name}")
        print(f"Category: {self.category}")
        print(f"Team: {self.team}")
        print(f"Seed Mark: {self.seed_mark}")
        for meet, events in self.races.items():
            print(f"Meet: {meet}")
            print(f"  Events: {', '.join(events)}")
        print("------")


class Team:
    def __init__(self, name):
        self.name = name
        self.runners = {}

    def add_runner(self, runner):
        self.runners[runner.name] = runner

    def get_runner(self, name):
        return self.runners.get(name)

    def has_runner(self, name):
        return name in self.runners

    def show_all_runners(self):
        for runner in self.runners.values():
            runner.show_info()