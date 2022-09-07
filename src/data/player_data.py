import pandas as pd


class PlayerData:
    def __init__(self, first_name, last_name, season):
        print("placeholder")
        self._data_location = '../../data/historical_data/' + season + "/"
        self._first_name = first_name
        self._last_name = last_name
        self._season = season

    def get_player_id(self):
        player_id_path = self._data_location + 'player_idlist.csv'
        df = pd.read_csv(player_id_path)
        player_id = (df.loc[(df.first_name == self._first_name) & (df.second_name == self._last_name), "id"]).tolist()[0]
        return player_id

    def get_player_id_string(self):
        player_id = self.get_player_id()
        player_id_string = self._first_name + "_" + self._last_name + "_" + str(player_id)
        return player_id_string

    def get_player_historical_seasons_statistics(self):
        player_id = self.get_player_id_string()
        historical_player_data_path = self._data_location + '/players/' + player_id + '/history.csv'
        df = pd.read_csv(historical_player_data_path)

        return df

    def get_player_current_seasons_statistics(self, game_week):
        if game_week == 0: return None
        player_id = self.get_player_id_string()
        historical_player_data_path = self._data_location + '/players/' + player_id + '/gw.csv'
        df = pd.read_csv(historical_player_data_path)
        df = df.head(game_week)

        return df

    def get_player_team_id(self):
        player_id = self.get_player_id()
        player_id_path = self._data_location + 'players_raw.csv'
        df = pd.read_csv(player_id_path)
        team_id = (df.loc[df.id == player_id, "team"]).tolist()[0]
        return team_id

    def get_player_points_earned(self, game_week):
        game = self.get_player_current_seasons_statistics(game_week).tail(1)
        points_earned = game["total_points"].tolist()[0]
        return points_earned

    def is_player_home(self, game_week):
        game = self.get_player_current_seasons_statistics(game_week).tail(1)
        home_or_away = game["was_home"].tolist()[0]
        return home_or_away


