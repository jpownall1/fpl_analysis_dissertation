from src.data.season_data import SeasonData
from src.data.player_data import PlayerData
from IPython.display import display
import pandas as pd


def calculate_players_total_points(players_df):
    total_points = players_df['total_points'].sum()
    return total_points


def calculate_teams_performance(season, position, subs, parameter="", operator="", value=""):
    if subs & (not operator or not parameter or not value): raise ValueError("If making subs, specify a parameter, "
                                                                             "operator and value")

    condition = parameter + operator + value

    # define player data object to obtain player data
    player_data = PlayerData(season)
    players_df = player_data.select_random_players(3, position)[['name', 'total_points', 'position', 'GW', parameter]]

    # make sure position is upper case
    position = position.upper()

    points_track = [calculate_players_total_points(players_df)]

    gameweeks = sorted(player_data.get_all_players_curr_season_merged_gw_stats()['GW'].unique())
    for gameweek in gameweeks:
        # if there is a duplicate of a player (as sometimes a player has to play twice in a game week as a result
        # of a missed game) then keep the final one for this iteration
        players_df = players_df.drop_duplicates(subset=['name'], keep='last')

        # obtain a dataframe of all players for that gameweek
        all_players_df = player_data.get_all_players_curr_season_gw_stats(gameweek)[['name', 'total_points',
                                                                                     'position', 'GW', parameter]]

        # select only players of the position in question
        all_players_df = all_players_df[all_players_df.eval(f"position == '{position}'")]

        # get a list of the names already in the df
        players_names_list = players_df["name"].values

        # update current players who feature in that gameweek with their new gameweek stats
        players_in_gw_df = all_players_df[all_players_df['name'].isin(players_names_list)]

        # for players who dont feature in that gameweek, update prev stats and set points to 0
        players_in_gw_names = players_in_gw_df["name"].values
        players_not_in_gw_df = players_df[~players_df['name'].isin(players_in_gw_names)]
        players_not_in_gw_df["total_points"] = 0

        # add these back together
        players_df = pd.concat([players_in_gw_df, players_not_in_gw_df])

        # remove players already in players df from all players
        all_players_df = all_players_df[~all_players_df['name'].isin(players_names_list)]

        # find a player who does not meet condition, if there is one remove and add a player from all players who does
        if subs:
            players_not_meeting_condition = players_df.query("~(" + condition + ")")
            if not players_not_meeting_condition.empty:
                player_to_remove = players_not_meeting_condition.sample(1).iloc[0]['name']
                players_df = players_df.drop(players_df[players_df['name'] == player_to_remove].index)
                # players_df = players_df.drop(player_to_remove.index[0])
                players_meeting_condition = all_players_df.query(condition)
                player_to_add = players_meeting_condition.sample(1)
                players_df = pd.concat([players_df, player_to_add])

        display(players_df)
        points_track.append(calculate_players_total_points(players_df))

    # alter points track to show accumulation of points
    for i in range(1, len(points_track)):
        points_track[i] = points_track[i - 1] + points_track[i]

    return points_track


print(calculate_teams_performance("2018-19", "MID", True, "was_home", "==", "True"))
