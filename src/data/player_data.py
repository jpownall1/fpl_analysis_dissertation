import pandas as pd


class PlayerData:
    def __init__(self, season):
        print("placeholder")
        self._data_location = '../../data/historical_data/' + season + "/"
        self._available_seasons = ["2016-17", "2017-18", "2018-19", "2019-20", "2020-21", "2021-22"]
        if season not in self._available_seasons:
            raise ValueError(f"Season {season} is unavailable. Please choose from the following seasons:"
                             f"{self._available_seasons}")
        else:
            self._season = season

    def get_player_id(self, first_name, last_name):
        player_id_path = self._data_location + 'player_idlist.csv'
        df = pd.read_csv(player_id_path)
        player_id = (df.loc[(df.first_name == self.first_name) & (df.second_name == self.last_name), "id"]).tolist()[0]
        return player_id

    def get_player_id_string(self, first_name, last_name):
        player_id = self.get_player_id(first_name, last_name)
        player_id_string = self.first_name + "_" + self.last_name + "_" + str(player_id)
        return player_id_string

    def get_player_historical_seasons_statistics(self, first_name, last_name):
        player_id = self.get_player_id_string(first_name, last_name)
        historical_player_data_path = self._data_location + '/players/' + player_id + '/history.csv'
        df = pd.read_csv(historical_player_data_path)

        return df

    def get_player_current_seasons_statistics(self, first_name, last_name, game_week):
        if game_week == 0: return None
        player_id = self.get_player_id_string(first_name, last_name)
        historical_player_data_path = self._data_location + '/players/' + player_id + '/gw.csv'
        df = pd.read_csv(historical_player_data_path)
        df = df.head(game_week)

        return df

    def get_player_team_id(self, first_name, last_name):
        player_id = self.get_player_id(first_name, last_name)
        player_id_path = self._data_location + 'players_raw.csv'
        df = pd.read_csv(player_id_path)
        team_id = (df.loc[df.id == player_id, "team"]).tolist()[0]
        return team_id

    def get_player_points_earned(self, first_name, last_name, game_week):
        game = self.get_player_current_seasons_statistics(first_name, last_name, game_week).tail(1)
        points_earned = game["total_points"].tolist()[0]
        return points_earned

    def is_player_home(self, first_name, last_name, game_week):
        game = self.get_player_current_seasons_statistics(first_name, last_name, game_week).tail(1)
        home_or_away = game["was_home"].tolist()[0]
        return home_or_away

    def get_all_players_gw_stats(self, game_week):

        data_location = self._data_location + "gws/gw" + str(game_week) + ".csv"
        df = pd.read_csv(data_location, encoding = "ISO-8859-1")
        return df

    def get_all_players_prev_season_stats(self):


        #changes data location to previous season
        season = self._season[:2] + str((int(self._season[2:4])-1)) + "-" + str((int(self._season[-2:])-1))

        data_location = self._data_location + "cleaned_players.csv"
        df = pd.read_csv(data_location, encoding = "ISO-8859-1")
        return df

    def get_all_players_curr_season_stats(self):
        data_location = '../../data/historical_data/' + self._season + "/"
        data_location = data_location + "cleaned_players.csv"
        df = pd.read_csv(data_location, encoding="ISO-8859-1")
        return df


