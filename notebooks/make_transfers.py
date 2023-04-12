import numpy as np
# from line_profiler_pycharm import profile

from src.data.player_data import PlayerData
from IPython.display import display
import pandas as pd
from notebooks.pick_team_lp import *
from notebooks.utils import select_initial_starting_11, organise_team

# set the max_columns option to None
pd.set_option('display.max_columns', None)


def calculate_players_performance_random(player_data: PlayerData, initial_players_df, position, transfers, parameter="",
                                         operator="",
                                         value="", display_changes=False):
    if transfers & (not operator or not parameter or not value):
        raise ValueError("If making transfers, specify a parameter, operator and value")

    # define player data object to obtain player data
    players_df = initial_players_df[['name', 'total_points', 'position', 'GW']].copy()
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

        players_df = update_players_stats(players_df, all_players_df)

        # find a player who does not meet condition, if there is one remove and add a player from all players who does
        if transfers:
            condition = create_condition(parameter, operator, value, players_df)
            players_df = transfer_player_random(condition, all_players_df, players_df, gameweek,
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


def calculate_teams_performance(player_data: PlayerData, initial_players_df, variable="",
                                display_changes=False, left_over_budget=0):
    # Check if there are 15 players in the squad
    if initial_players_df.shape[0] != 15:
        print(f"The team has {initial_players_df.shape[0]} players, but the desired number of players is {15}.")

    # define player data object to obtain player data
    players_df = initial_players_df[['name', 'minutes', 'kickoff_time', 'total_points', 'position', 'GW', 'value', variable]].copy()

    # helpful console output for initial team display
    if display_changes:
        print("--------------------------------- INITIAL TEAM ---------------------------------")
        display(players_df)

    # initialise points track
    points_track = []

    # get an array of gameweek values (as some don't go 1-38) and sort
    gameweeks = sorted(player_data.get_all_players_all_gw_stats()['GW'].unique())

    # For each gameweek, make a transfer if specified, and update points
    for gameweek in gameweeks:
        # obtain a dataframe of all players for that gameweek
        all_players_df = player_data.get_all_players_gw_stats(gameweek)[['name', 'minutes', 'kickoff_time', 'total_points',
                                                                         'position', 'GW', 'value',
                                                                         variable]]

        # update stats for players in gameweek
        players_df = update_players_stats(players_df, all_players_df)

        # find a player who makes the biggest change in predicted points, if there is one remove and add a player
        # from all players who does
        delta_predicted_points = find_highest_positive_delta_predicted_points(players_df, all_players_df,
                                                                              left_over_budget)
        player_to_transfer_out = delta_predicted_points[0]
        player_to_transfer_in = delta_predicted_points[1]
        left_over_budget = delta_predicted_points[2]
        players_df = transfer_player(players_df, player_to_transfer_in, player_to_transfer_out, True, gameweek, left_over_budget)

        starting_df, subs_df = organise_team(players_df, "predicted_points")
        points_track.append(calculate_players_total_points(starting_df))

        # error check
        check_team_size(players_df, initial_players_df)

    # helpful console output for final team display
    if display_changes:
        print("--------------------------------- FINAL TEAM ---------------------------------")
        display(players_df)

    # alter points track to show accumulation of points
    points_track = accumulate_points(points_track)

    return np.asarray(points_track)


def display_transfer(left_over_budget, player_to_add, player_to_remove, gameweek):
    # helpful console output for when the changes make place
    print(f"---------------------- Gameweek:{gameweek} ----------------------")
    print("PLAYER TRANSFERRED OUT:")
    display(player_to_remove)
    print("PLAYER TRANSFERRED IN:")
    display(player_to_add)
    print("BUDGET:")
    print(left_over_budget)


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


def update_players_stats(players_df, all_players_df):
    # get a list of the names already in the df
    players_names_list = players_df["name"].values

    # update current players who feature in that gameweek with their new gameweek stats
    players_in_gw_df = all_players_df[all_players_df['name'].isin(players_names_list)].drop_duplicates(
        subset=['name'], keep='last', ignore_index=True)

    # for players who don't feature in that gameweek, update prev stats by setting points to 0
    players_in_gw_names = players_in_gw_df["name"].values
    players_df.loc[~players_df['name'].isin(players_in_gw_names), 'total_points'] = 0

    # update players_df with the new total_points from players_in_gw_df
    players_df.set_index('name', inplace=True)
    players_in_gw_df.set_index('name', inplace=True)
    players_df.update(players_in_gw_df)
    players_df.reset_index(inplace=True)

    return players_df


def transfer_player_random(condition, all_players_df, players_df, gameweek, display_changes):
    # get a list of the names already in the df
    players_names_list = players_df["name"].values

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


def transfer_player(players_df, player_transfer_in, player_transfer_out, display_changes, gameweek, left_over_budget):
    # Find the index of the player_transfer_out in the players_df
    transfer_out_index = players_df[players_df['name'] == player_transfer_out['name'].values[0]].index[0]

    # Drop the player_transfer_out from players_df
    players_df = players_df.drop(transfer_out_index).reset_index(drop=True)

    # Add the player_transfer_in to players_df
    players_df = pd.concat([players_df, player_transfer_in], ignore_index=True)

    if display_changes:
        display_transfer(left_over_budget, player_transfer_in, player_transfer_out, gameweek)

    return players_df


def find_highest_positive_delta_predicted_points(players_df, all_players_df, left_over_budget):
    highest_positive_delta_player = None
    highest_positive_delta_value = float('-inf')
    highest_predicted_points_player = None

    # Get the list of player names from players_df
    players_df_names = players_df['name'].tolist()

    # Iterate through each player in the 15-player DataFrame
    for index, player in players_df.iterrows():
        player_value = player['value'] + left_over_budget
        player_gameweek = player['GW']
        player_position = player['position']

        # Filter all_players_df based on the player's value (including left_over_budget), the next gameweek, and position
        filtered_players = all_players_df[(all_players_df['value'] <= player_value) &
                                          (all_players_df['GW'] == player_gameweek) &
                                          (all_players_df['position'] == player_position) &
                                          (~all_players_df['name'].isin(players_df_names))]

        # Find the highest predicted points among the filtered players
        highest_predicted_points = filtered_players['predicted_points'].max()

        # Calculate delta_predicted_points for the current player
        delta_predicted_points = highest_predicted_points - player['predicted_points']

        # Update the highest_positive_delta_player and the highest_predicted_points_player if needed
        if delta_predicted_points > highest_positive_delta_value and delta_predicted_points > 0:
            highest_positive_delta_value = delta_predicted_points
            highest_positive_delta_player = players_df.loc[[index]]
            highest_predicted_points_player = filtered_players.loc[[filtered_players['predicted_points'].idxmax()]]

    # Update left_over_budget after choosing the player with the highest positive delta
    left_over_budget += highest_positive_delta_player['value'].values[0] - \
                        highest_predicted_points_player['value'].values[0]

    return highest_positive_delta_player, highest_predicted_points_player, left_over_budget


def check_team_size(players_df, initial_players_df):
    if players_df.shape[0] != initial_players_df.shape[0]:
        raise ValueError(f"""Final team does not have correct amount of players. Something has gone wrong.
                             Number of players has been changed from {initial_players_df.shape[0]} to {players_df.shape[0]} 
                             {display(players_df)}""")


def accumulate_points(points_track):
    for i in range(1, len(points_track)):
        points_track[i] = points_track[i - 1] + points_track[i]
    return points_track


if __name__ == "__main__":
    # demonstration
    player_data = PlayerData("2021-22")
    position = "mid"
    random_players_df = player_data.select_random_players_from_gw_one(5, position)
    print(calculate_players_performance_random(player_data, random_players_df, position, True, "recent_total_points",
                                               ">", "lowest", True))
