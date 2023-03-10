import numpy as np
# from line_profiler_pycharm import profile

from src.data.player_data import PlayerData
from IPython.display import display
import pandas as pd


def calculate_teams_performance(player_data: PlayerData, initial_players_df, position, transfers, parameter="",
                                operator="",
                                value="", display_changes=False):
    if transfers & (not operator or not parameter or not value):
        raise ValueError("If making transfers, specify a parameter, operator and value")

    # define player data object to obtain player data
    players_df = initial_players_df[['name', 'total_points', 'position', 'GW']]
    if transfers:
        players_df[parameter] = initial_players_df[parameter]

    # helpful console output for initial team display
    if display_changes:
        print("--------------------------------- INITIAL TEAM ---------------------------------")
        display(players_df)

    # make sure position is upper case
    position = position.upper()

    # initialise points track with points gained from gw 1 for intial team
    points_track = [calculate_players_total_points(players_df)]

    # get an array of gameweek values (as some don't go 1-38) and sort
    gameweeks = sorted(player_data.get_all_players_all_gw_stats()['GW'].unique())
    # Remove first week as the points are already in the array
    gameweeks.pop(0)

    # For each gameweek, make a transfer if specified, and update points
    for gameweek in gameweeks:
        # obtain a dataframe of all players for that gameweek
        if transfers:
            all_players_df = player_data.get_position_players_gw_stats(gameweek, position)[['name', 'total_points',
                                                                                            'position', 'GW',
                                                                                            parameter]]
        else:
            all_players_df = player_data.get_position_players_gw_stats(gameweek, position)[['name', 'total_points',
                                                                                            'position', 'GW']]

        # get a list of the names already in the df
        players_names_list = players_df["name"].values

        players_df = update_players_stats(players_df, all_players_df, players_names_list)

        # find a player who does not meet condition, if there is one remove and add a player from all players who does
        if transfers:
            condition = create_condition(parameter, operator, value, players_df)
            players_df = transfer_player(condition, all_players_df, players_df, gameweek, players_names_list,
                                         display_changes)

        points_track.append(calculate_players_total_points(players_df))

        # error check
        check_team_size(players_df, initial_players_df)

    # helpful console output for final team display
    if display_changes:
        print("--------------------------------- FINAL TEAM ---------------------------------")
        display(players_df)

    # alter points track to show accumulation of points
    points_track = accumulate_points(points_track)

    return np.asarray(points_track)


def display_transfer(current_team, player_to_add, player_to_remove, gameweek):
    # helpful console output for when the changes make place
    print(f"---------------------- Gameweek:{gameweek} ----------------------")
    print("CURRENT TEAM")
    print(current_team)
    print("PLAYER TRANSFERRED OUT:")
    display(player_to_remove)
    print("PLAYER TRANSFERRED IN:")
    display(player_to_add)


def calculate_players_total_points(players_df):
    total_points = players_df['total_points'].sum()
    return total_points


def create_condition(parameter, operator, value, players_df):
    if parameter != "was_home":
        if value == "highest":
            value = players_df[parameter].max()
        elif value == "lowest":
            value = players_df[parameter].min()
    condition = parameter + operator + str(value)
    return condition


def update_players_stats(players_df, all_players_df, players_names_list):
    # update current players who feature in that gameweek with their new gameweek stats
    players_in_gw_df = all_players_df[all_players_df['name'].isin(players_names_list)].drop_duplicates(
        subset=['name'], keep='last', ignore_index=True)

    # for players who don't feature in that gameweek, update prev stats by setting points to 0
    players_in_gw_names = players_in_gw_df["name"].values
    players_not_in_gw_df = players_df[~players_df['name'].isin(players_in_gw_names)]
    players_df.loc[~players_df['name'].isin(players_in_gw_names), 'total_points'] = 0

    # add these back together
    players_df = pd.concat([players_in_gw_df, players_not_in_gw_df])
    return players_df


def transfer_player(condition, all_players_df, players_df, gameweek, players_names_list, display_changes):
    players_not_meeting_condition = players_df[players_df.eval("~(" + condition + ")")]
    if not players_not_meeting_condition.empty:
        # remove players already in players df from all players
        all_players_df = all_players_df[~all_players_df['name'].isin(players_names_list)]
        players_meeting_condition = all_players_df[all_players_df.eval(condition)]
        if not players_meeting_condition.empty:
            # remove a player from the dataframe of players who do not meet the condition
            player_to_remove = players_not_meeting_condition.sample(1)
            players_df = pd.concat([players_df, player_to_remove, player_to_remove]).drop_duplicates(subset=['name'],
                                                                                                     keep=False)

            # add a player from the pool of players available to be transferred who meet the condition
            player_to_add = players_meeting_condition.sample(1)
            players_df = pd.concat([players_df, player_to_add])

            if display_changes:
                display_transfer(players_df, player_to_add, player_to_remove, gameweek)
    return players_df


def check_team_size(players_df, initial_players_df):
    if players_df.shape[0] != initial_players_df.shape[0]:
        raise ValueError(f"""Final team does not have correct amount of players. Something has gone wrong.
                             Number of players has been changed from {initial_players_df.shape[0]} to {players_df.shape[0]} 
                             {display(players_df)}""")


def accumulate_points(points_track):
    for i in range(1, len(points_track)):
        points_track[i] = points_track[i - 1] + points_track[i]
    return points_track


# define player data object to obtain player data
player_data = PlayerData("2021-22")
position = "mid"
random_players_df = player_data.select_random_players_from_gw_one(5, position)
print(calculate_teams_performance(player_data, random_players_df, position, True, "recent_total_points", ">", "lowest", True))
