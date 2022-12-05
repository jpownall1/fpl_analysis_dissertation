import pandas as pd
from season_data import SeasonData

class TeamData:
    def __init__(self, team_id, season):
        print("placeholder")
        self._data_location = '../../data/' + season + "/"
        self._season = season
        self._team_id = team_id
        self._season_data = SeasonData(season)

    def get_team_name(self):
        path = self._data_location + 'teams.csv'
        df = pd.read_csv(path)
        team = df[(df["id"] == self._team_id)]
        return team["name"].tolist()[0]


    def get_team_fixtures(self):
        df = self._season_data.get_fixtures()
        df = df[(df["team_a"] == self._team_id) | (df["team_h"] == self._team_id)]
        return df

    def get_gameweek_fixture(self, gameweek):
        df = self.get_team_fixtures()
        fixture = df[df["event"] == gameweek]
        return fixture

    def is_home(self, gameweek):
        game = self.get_gameweek_fixture(gameweek)
        if game["team_h"].tolist()[0] == self._team_id:
            return True
        else:
            return False

    def get_opponent_id(self, gameweek):
        game = self.get_gameweek_fixture(gameweek)
        if self.is_home(gameweek):
            opponent_id = game["team_a"].tolist()[0]
        else:
            opponent_id = game["team_h"].tolist()[0]
        return opponent_id

    def get_opponent_name(self, gameweek):
        path = self._data_location + 'teams.csv'
        df = pd.read_csv(path)
        opponent_id = self.get_opponent_id(gameweek)
        team = df[(df["id"] == opponent_id)]
        opponent_name = team["name"].tolist()[0]
        return opponent_name

    def favourite_to_win(self, gameweek):
        game = self.get_gameweek_fixture(gameweek)
        if self.is_home(gameweek):
            team_difficulty = game["team_h_difficulty"].tolist()[0]
            opponent_difficulty = game["team_a_difficulty"].tolist()[0]
        else:
            opponent_difficulty = game["team_h_difficulty"].tolist()[0]
            team_difficulty = game["team_a_difficulty"].tolist()[0]

        if team_difficulty < opponent_difficulty:
            return True
        else:
            return False
