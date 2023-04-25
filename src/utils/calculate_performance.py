"""
calculate_performance.py: A module that provides functions to simulate the performance of a fantasy football team.

This module contains functions for calculating the performance of a team of players over a season using different
strategies. It provides methods for simulating the performance of a team with random transfers, as well as a method for
calculating the performance using the official FPL rules.

Functions:
    - calculate_players_performance_random: Simulates a random player performance calculation based on given parameters.
    - calculate_teams_performance: Calculates the performance of a team over the season, making transfers based on a
                                   given variable, adhering to the FPL official rules.
    - calculate_players_total_points: Calculates the total points for a given team of players.
    - create_condition: Returns a string condition based on the given parameter, operator, value, and players DataFrame.
    - update_players_stats: Update the stats of the players in players_df using the latest gameweek stats from
                            all_players_df.
    - accumulate_points: Calculate the cumulative points for each gameweek in the given points track.
"""

import numpy as np
from src.utils.make_transfers import transfer_player_random, transfer_player
from src.utils.organise_team import organise_team
from src.utils.utils import check_team_size
from src.data.player_data import PlayerData


def calculate_players_performance_random(player_data: PlayerData, initial_players_df, position, transfers, parameter="",
                                         operator="",
                                         value="", display_changes=False):
    """
    Simulates a random player performance calculation based on the given parameters.

    Args:
        player_data (PlayerData): An object that holds player data.
        initial_players_df (pd.DataFrame): A dataframe containing the initial players.
        position (str): The position of the players to consider (e.g., 'FWD', 'MID', 'DEF', 'GK').
        transfers (bool): A flag to indicate if transfers should be made or not.
        parameter (str, optional): The parameter to consider when making transfers. Defaults to an empty string.
        operator (str, optional): The operator to use when comparing the parameter value. Defaults to an empty string.
        value (str, optional): The value to compare with the parameter using the operator. Defaults to an empty string.
        display_changes (bool, optional): A flag to indicate if changes should be displayed. Defaults to False.

    Returns:
        np.ndarray: An array representing accumulated points for each gameweek.

    Raises:
        ValueError: If transfers are True and parameter, operator, or value is not specified.
    """
    if transfers & (not operator or not parameter or not value):
        raise ValueError("If making transfers, specify a parameter, operator and value")

    # Define player data object to obtain player data
    players_df = initial_players_df[['name', 'total_points', 'position', 'GW']].copy()
    if transfers:
        players_df[parameter] = initial_players_df[parameter]

    # Helpful console output for initial team display
    if display_changes:
        print("--------------------------------- INITIAL TEAM ---------------------------------")
        print(players_df)

    # Make sure position is upper case
    position = position.upper()

    # Initialise points track with points gained from gw 1 for intial team
    points_track = [calculate_players_total_points(players_df)]

    # Get an array of gameweek values (as some don't go 1-38) and sort
    gameweeks = sorted(player_data.get_all_players_all_gw_stats()['GW'].unique())
    # Remove first week as the points are already in the array
    gameweeks.pop(0)

    # For each gameweek, make a transfer if specified, and update points
    for gameweek in gameweeks:
        # Obtain a dataframe of all players for that gameweek
        if transfers:
            all_players_df = player_data.get_position_players_gw_stats(gameweek, position)[['name', 'total_points',
                                                                                            'position', 'GW',
                                                                                            parameter]]
        else:
            all_players_df = player_data.get_position_players_gw_stats(gameweek, position)[['name', 'total_points',
                                                                                            'position', 'GW']]

        players_df = update_players_stats(players_df, all_players_df)

        # Find a player who does not meet condition, if there is one remove and add a player from all players who does
        if transfers:
            condition = create_condition(parameter, operator, value, players_df)
            players_df = transfer_player_random(condition, all_players_df, players_df, gameweek,
                                                display_changes)

        points_track.append(calculate_players_total_points(players_df))

        # Error check
        check_team_size(players_df, initial_players_df)

    # Helpful console output for final team display
    if display_changes:
        print("--------------------------------- FINAL TEAM ---------------------------------")
        print(players_df)

    # alter points track to show accumulation of points
    points_track = accumulate_points(points_track)

    return np.asarray(points_track)


def calculate_teams_performance(player_data: PlayerData, initial_players_df, variable="",
                                display_changes=False, left_over_budget=0):
    """
        Calculates the performance of a team over the season, making transfers based on the given variable, adhering to
        the FPL official rules.

        Args:
            player_data (PlayerData): An object that holds player data.
            initial_players_df (pd.DataFrame): A dataframe containing the initial players.
            variable (str, optional): The variable to consider when making transfers. Defaults to an empty string.
            display_changes (bool, optional): A flag to indicate if changes should be displayed. Defaults to False.
            left_over_budget (int or float, optional): The remaining budget for the team. Defaults to 0.

        Returns:
            np.ndarray: An array representing accumulated points for each gameweek.

        Note:
            The method raises a warning if there are not exactly 15 players in the initial_players_df.
        """
    # Check if there are 15 players in the squad
    if initial_players_df.shape[0] != 15:
        print(f"The team has {initial_players_df.shape[0]} players, but the desired number of players is {15}.")

    # Store initial 'bought for' value
    initial_players_df['bought_for'] = initial_players_df['value'].copy()

    # Define player data object to obtain player data
    players_df = initial_players_df[
        ['name', 'minutes', 'kickoff_time', 'total_points', 'position', 'GW', 'bought_for', 'value', "team", variable]].copy()

    # Helpful console output for initial team display
    if display_changes:
        print("--------------------------------- INITIAL TEAM ---------------------------------")
        print(players_df)

    # initialise points track
    points_track = []

    # get an array of gameweek values (as some don't go 1-38) and sort
    gameweeks = sorted(player_data.get_all_players_all_gw_stats()['GW'].unique())

    # For each gameweek, make a transfer if specified, and update points
    for gameweek in gameweeks:
        # obtain a dataframe of all players for that gameweek
        all_players_df = player_data.get_all_players_gw_stats(gameweek)[
            ['name', 'minutes', 'kickoff_time', 'total_points',
             'position', 'GW', 'value', "team",
             variable]]

        # Update stats for players in gameweek
        players_df = update_players_stats(players_df, all_players_df)

        # Transfer player
        players_df, left_over_budget, delta_value, player_transferred_out, \
        player_transferred_in, change_in_actual_points = transfer_player(all_players_df, players_df, display_changes,
                                                                         gameweek, left_over_budget)

        # Organise team and calculate points earnt
        starting_df, subs_df = organise_team(players_df, "predicted_points", display_changes)
        gw_total_points = calculate_players_total_points(starting_df)
        points_track.append(gw_total_points)

        # error check
        check_team_size(players_df, initial_players_df)

    # helpful console output for final team display
    if display_changes:
        print("--------------------------------- FINAL TEAM ---------------------------------")
        print(players_df)

    # alter points track to show accumulation of points
    points_track = accumulate_points(points_track)

    return np.asarray(points_track)


def calculate_players_total_points(players_df, display=False):
    """
    Calculates the total points for a given team of players.

    Args:
        players_df (pd.DataFrame): A dataframe containing player information, including 'total_points' column.
        display (bool, optional): A flag to indicate if the total points should be printed. Defaults to False.

    Returns:
        int: The sum of total points for all players in the team.
    """
    total_points = players_df['total_points'].sum()
    if display:
        print(f"Total team points: {total_points}")
    return total_points


def create_condition(parameter, operator, value, players_df):
    """
    Returns a string condition based on the given parameter, operator, value, and players DataFrame.
    """
    if parameter != "was_home":
        if value == "highest":
            value = players_df[parameter].max()
        elif value == "lowest":
            value = players_df[parameter].min()
    condition = parameter + operator + str(value)
    return condition


def update_players_stats(players_df, all_players_df):
    """
        Update the stats of the players in players_df using the latest gameweek stats from all_players_df.

        Args:
            players_df (pd.DataFrame): A DataFrame containing the current stats of the players.
            all_players_df (pd.DataFrame): A DataFrame containing the latest gameweek stats of all players.

        Returns:
            pd.DataFrame: A DataFrame containing the updated stats of the players.
        """
    # get a list of the names already in the df
    players_names_list = players_df["name"].values

    # update current players who feature in that gameweek with their new gameweek stats
    players_in_gw_df = all_players_df[all_players_df['name'].isin(players_names_list)].drop_duplicates(
        subset=['name'], keep='last', ignore_index=True)

    # for players who don't feature in that gameweek, update prev stats by setting points to 0
    players_in_gw_names = players_in_gw_df["name"].values
    players_df.loc[~players_df['name'].isin(players_in_gw_names), 'total_points'] = 0
    # Also set predicted points to 0 for these players. This results in players who dont play some games being
    # transferred out
    players_df.loc[~players_df['name'].isin(players_in_gw_names), 'predicted_points'] = 0

    # update players_df with the new total_points from players_in_gw_df
    players_df.set_index('name', inplace=True)
    players_in_gw_df.set_index('name', inplace=True)

    # Save the 'bought_for' values before updating
    bought_for_values = players_df['bought_for'].copy()

    # Update players_df with players_in_gw_df
    players_df.update(players_in_gw_df)

    # Reassign the 'bought_for' values after updating
    players_df['bought_for'] = bought_for_values

    players_df.reset_index(inplace=True)

    return players_df



def accumulate_points(points_track):
    """
    Calculate the cumulative points for each gameweek in the given points track.

    Args:
        points_track (List[int]): A list of points for each gameweek.

    Returns:
        List[int]: A list of the cumulative points for each gameweek.
    """
    for i in range(1, len(points_track)):
        points_track[i] = points_track[i - 1] + points_track[i]
    return points_track


if __name__ == "__main__":
    # demonstration for random
    player_data = PlayerData("2021-22")
    position = "mid"
    random_players_df = player_data.select_random_players_from_gw_one(5, position)
    print(calculate_players_performance_random(player_data, random_players_df, position, True, "recent_total_points",
                                               ">", "lowest", True))
