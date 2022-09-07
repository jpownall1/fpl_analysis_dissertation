import pandas as pd
from season_data import SeasonData

class TeamData:
    def __init__(self, team_id, season):
        print("placeholder")
        self._data_location = '../../data/historical_data/' + season + "/"
        self._season = season
        self._team_id = team_id
        self._season_data = SeasonData(season)


    def get_teams_fixtures(self):
        df = self._season_data.get_fixtures()
        df = df[df["team_a"] == self._team_id | df["team_h"] == self._team_id]
        return df

    def get_gameweek_fixture(self, gameweek):
        df = self._season_data.get_gameweek_fixtures(gameweek)
        df = df[df["team_a"] == self._team_id | df["team_h"] == self._team_id]
        return df
