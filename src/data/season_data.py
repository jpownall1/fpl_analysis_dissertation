import pandas as pd


class SeasonData:
    def __init__(self, season):
        print("placeholder")
        self._data_location = '../../data/historical_data/' + season + "/"
        self._season = season

    def get_teams(self):
        path = self._data_location + 'teams.csv'
        df = pd.read_csv(path)
        return df

    def get_fixtures(self):
        path = self._data_location + 'fixtures.csv'
        df = pd.read_csv(path)
        return df

    def get_gameweek_fixtures(self, gameweek):
        df = self.get_fixtures(self)
        df = df[df["event"] == gameweek]
        return df


