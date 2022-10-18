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
        df = self.get_fixtures()
        df = df[df["event"] == gameweek]
        return df

    def get_all_players_gw_stats(self, game_week):

        data_location = self._data_location + "gws/gw" + str(game_week) + ".csv"
        df = pd.read_csv(data_location, encoding = "ISO-8859-1")
        return df

    def get_all_players_prev_season_stats(self):
        #changes data location to previous season
        season = self._season[:2] + str((int(self._season[2:4])-1)) + "-" + str((int(self._season[-2:])-1))
        data_location = '../../data/historical_data/' + season + "/"

        data_location = data_location + "cleaned_players.csv"
        df = pd.read_csv(data_location, encoding = "ISO-8859-1")
        return df

    def get_all_players_curr_season_stats(self):
        data_location = '../../data/historical_data/' + self._season + "/"
        data_location = data_location + "cleaned_players.csv"
        df = pd.read_csv(data_location, encoding="ISO-8859-1")
        return df



