import pandas as pd
from IPython.core.display_functions import display
from pathlib import Path


# from line_profiler_pycharm import profile


class PlayerData:
    def __init__(self, season):
        print("placeholder")
        self._data_location = str(Path(__file__).parent) + '/../../data/' + season + "/"
        self._available_seasons = ["2016-17", "2017-18", "2018-19", "2019-20", "2020-21", "2021-22"]
        self._parameters = ["no_subs", "subs_on_was_home", "subs_on_was_away", "subs_on_higher_recent_total_points",
                            "subs_on_higher_recent_goals_scored", "subs_on_higher_recent_yellow_cards",
                            "subs_on_lower_recent_yellow_cards", "subs_on_higher_recent_red_cards",
                            "subs_on_lower_recent_red_cards",
                            "subs_on_higher_recent_assists", "subs_on_higher_recent_clean_sheets",
                            "subs_on_higher_recent_saves",
                            "subs_on_higher_recent_minutes", "subs_on_higher_recent_bps",
                            "subs_on_higher_recent_goals_conceded",
                            "subs_on_lower_recent_goals_conceded", "subs_on_higher_recent_creativity",
                            "subs_on_higher_recent_won_games"]
        if season not in self._available_seasons:
            raise ValueError(f"Season {season} is unavailable. Please choose from the following seasons:"
                             f"{self._available_seasons}")
        else:
            self._season = season

        self._merged_gw_stats = None
        self._gw_stats_dict = None
        self._gw_pos_stats_dict = None
        self._gw_condition_stats_dict = None

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

    def get_all_players_prev_season_stats(self):

        # changes data location to previous season
        season = self._season[:2] + str((int(self._season[2:4]) - 1)) + "-" + str((int(self._season[-2:]) - 1))

        data_location = self._data_location + "cleaned_players.csv"
        df = pd.read_csv(data_location, encoding="utf-8")
        return df

    def get_all_players_total_curr_season_stats(self):
        data_location = self._data_location + "cleaned_players.csv"
        df = pd.read_csv(data_location, encoding="utf-8")
        return df

    def get_all_players_all_gw_stats(self):
        if self._merged_gw_stats is None:
            data_location = self._data_location + "/gws/merged_gw2.csv"
            self._merged_gw_stats = pd.read_csv(data_location, encoding="utf-8")

        df = self._merged_gw_stats
        return df

    def get_all_players_gw_stats(self, gameweek):
        if self._gw_stats_dict is None:
            merged_gw_df = self.get_all_players_all_gw_stats()
            self._gw_stats_dict = {gw: df for gw, df in merged_gw_df.groupby("GW")}

        df = self._gw_stats_dict[gameweek]
        return df

    def get_position_players_gw_stats(self, gameweek, position):
        if self._gw_pos_stats_dict is None:
            self._gw_pos_stats_dict = {}

        if gameweek not in self._gw_pos_stats_dict:
            gw_df = self.get_all_players_gw_stats(gameweek)
            self._gw_pos_stats_dict[gameweek] = {}
            self._gw_pos_stats_dict[gameweek]["FWD"] = gw_df[gw_df["position"] == "FWD"]
            self._gw_pos_stats_dict[gameweek]["MID"] = gw_df[gw_df["position"] == "MID"]
            self._gw_pos_stats_dict[gameweek]["DEF"] = gw_df[gw_df["position"] == "DEF"]
            self._gw_pos_stats_dict[gameweek]["GK"] = gw_df[gw_df["position"] == "GK"]

        return self._gw_pos_stats_dict[gameweek][position]

    def get_players_meeting_condition_or_not(self, gameweek, condition, meeting):
        if self._gw_condition_stats_dict is None:
            self._gw_condition_stats_dict = {}
            self._gw_condition_stats_dict[condition] = {}
            df = self.get_all_players_gw_stats(gameweek)
            players_not_meeting_condition = df[~df.eval(condition)]
            players_meeting_condition = df[df.eval(condition)]
            self._gw_condition_stats_dict[condition]["nm"] = players_not_meeting_condition
            self._gw_condition_stats_dict[condition]["m"] = players_meeting_condition

        if meeting:
            return self._gw_condition_stats_dict[condition]["m"]
        else:
            return self._gw_condition_stats_dict[condition]["nm"]

    def select_random_players_from_gw_one(self, number_of_players, position):
        """
        Randomly select a certain number of players from game week 1 players of a certain position.

        Parameters
        ----------
        number_of_players: the number of players to select satisfying the condition,
        position: the position for the players to satisfy, e.g. MID

        Returns
        ----------
        players: a random sample of players satisfying the specified condition

        Examples
        ----------
        Selects 3 midfielders at random from the specified season
        selected_rows = select_samples(df, 3, "position == 'MID'")
        """
        # make sure position is upper case
        position = position.upper()

        # obtain a dataframe of all players for that season
        all_players_df = self.get_all_players_gw_stats(1)

        # randomly select 'number_of_players' players from this dataframe satisfying condition 'condition'
        players_df = all_players_df[all_players_df.eval(f"position == '{position}'")].sample(number_of_players)

        return players_df

    def is_player_in_gameweek(self, gameweek, name):
        players_df = self.get_all_players_gw_stats(gameweek)
        is_name_present = players_df['name'].isin([name]).any()
        return is_name_present