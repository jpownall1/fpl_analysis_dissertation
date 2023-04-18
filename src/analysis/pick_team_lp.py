"""
pick_team_lp.py

This module uses Linear Programming (LP) to optimize the selection of an initial Fantasy Premier League (FPL) team based
on historical player data.

Functions:
- get_historical_stats_with_curr_price(season): Retrieves a dataframe of filtered historical player stats combined with
                                                the current season's initial price.
- make_initial_team_lp(season): Uses LP to pick the initial team for a season based on historical points scored, budget,
                                and other constraints.
- update_players_stats(players_df, all_players_df, players_names_list): Updates the statistics of the players in the
                                                                        'players_df' dataframe with the statistics from
                                                                        the specified gameweek in the 'all_players_df'
                                                                        dataframe.
- convert_to_merged_gw_one(player_data, players_df): Merges the data of the players in 'players_df' with the statistics
                                                     from the first gameweek of the season.
- get_selected_players_gw_one_data(player_data, selected_player_names): Returns a dataframe containing the game week 1
                                                                        stats for the selected players.
"""

import pulp as pulp
from src.data.player_data import PlayerData
import pandas as pd


def get_historical_stats_with_curr_price(season):
    """
    Retrieves a Pandas dataframe of filtered, historical season player stats combined with current seasons inital
    price. Useful for using LP to pick a starter team based on previous points earnt and current price.

    params:
    season - season with the current price

    returns:
    merged_df - dataframe with previous seasons merged stats
    """
    # get previous seasons player stats
    players = PlayerData(season)
    last_s_data = players.get_all_players_prev_season_stats()
    last_s_data = last_s_data[['first_name', 'second_name', 'total_points', 'minutes', 'team_name', 'position']]
    # remove players who have not played around 30 games
    last_s_data = last_s_data.drop(last_s_data[last_s_data.minutes < 90 * 30].index)

    # get current season player stats
    this_s_data = players.get_all_players_total_curr_season_stats()
    this_s_data = this_s_data[['name', 'first_name', 'second_name', 'initial_cost', 'team_name', 'position']]

    # merge together, this eliminates players who are newly promoted or relegated
    # merging on team_name also eliminates players who have changed teams
    merged_df = pd.merge(last_s_data, this_s_data, on=["first_name", "second_name", 'team_name', 'position'])

    return merged_df


def make_initial_team_lp(season):
    """
    Uses linear programming python module PuLP to pick the initial team for a season based on amount of points
    scored historically with position, budget and team constraints.

    params:
    season - season to pick the team for

    returns:
    selected_players_names - a list of players names from the optimal team
    left_over_money - the amount of money left over from picking the team
    """
    # filtered dataframe
    data = get_historical_stats_with_curr_price(season)

    # constraint variables
    POS = data.position.unique()
    CLUBS = data.team_name.unique()
    BUDGET = 1000
    pos_available = {
        'DEF': 5,
        'FWD': 3,
        'MID': 5,
        'GK': 2
    }

    # Initialize Variables
    teams = [data.team_name[i] for i in data.index]
    positions = [data.position[i] for i in data.index]
    points = [data.total_points[i] for i in data.index]
    players = [pulp.LpVariable("player_" + str(i), cat="Binary") for i in data.index]

    # Initialize the problem
    prob = pulp.LpProblem("FPL Player Choices", pulp.LpMaximize)

    # Define the objective
    prob += pulp.lpSum(players[i] * points[i] for i in range(len(data)))

    # Build the constraints
    # constraint 1: Budget
    prob += pulp.lpSum(players[i] * data.initial_cost[data.index[i]] for i in range(len(data))) <= BUDGET

    # constraint 2: Position limit (2 for GK, 5 for DEF, 5 for MID, 3 for FWD)
    for pos in POS:
        prob += pulp.lpSum(players[i] for i in range(len(data)) if positions[i] == pos) <= pos_available[pos]

    # constraint 3: Clubs limit (maximum of 3 players from a single club)
    for club in CLUBS:
        prob += pulp.lpSum(players[i] for i in range(len(data)) if teams[i] == club) <= 3

    # Solve the problem
    prob.solve()

    # Collect the names of the selected players and calculate total price
    selected_player_names = []
    tot_price = 0
    for v in prob.variables():
        if v.varValue != 0:
            name = data.name[int(v.name.split("_")[1])]
            selected_player_names.append(name)
            price = data.initial_cost[int(v.name.split("_")[1])]
            tot_price += price

    left_over_money = BUDGET - tot_price
    return selected_player_names, left_over_money


def update_players_stats(players_df, all_players_df, players_names_list):
    """
    Updates the statistics of the players in the `players_df` dataframe with the statistics from the specified gameweek
    in the `all_players_df` dataframe. If a player in the `players_df` dataframe did not feature in the specified
    gameweek, their previous statistics are updated by setting their points to zero.

    Args:
        players_df (pd.DataFrame): The dataframe containing the players already selected.
        all_players_df (pd.DataFrame): The dataframe containing all the players' statistics.
        players_names_list (list): The list of names of the players already selected.
    Returns:
        pd.DataFrame: The updated dataframe containing the players already selected, with their statistics updated.
    """
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


def convert_to_merged_gw_one(player_data, players_df):
    """
    Merges the data of the players in `players_df` with the statistics from the first gameweek of the season.

    Args:
        player_data (PlayerData): The object containing the data for all the players.
        players_df (pd.DataFrame): The dataframe containing the players already selected.
    Returns:
        pd.DataFrame: The updated dataframe containing the players already selected with their statistics from the first
        gameweek of the season added.
    """
    # get a list of the names already in the df
    players_names_list = players_df["name"].values

    gw_one_df = player_data.get_all_players_gw_stats(1)

    updated_players_df = update_players_stats(players_df, gw_one_df, players_names_list)

    return updated_players_df


def get_selected_players_gw_one_data(player_data, selected_player_names):
    """
    Returns a pandas DataFrame containing the game week 1 stats for the selected players.

    Args:
        player_data (FplData): The FplData object that contains the data to be filtered.
        selected_player_names (List[str]): A list of player names to select the stats for.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the game week 1 stats for the selected players.
    """
    all_players_gw_data = player_data.get_all_players_gw_stats(1)
    selected_players_gw_data = all_players_gw_data[all_players_gw_data['name'].isin(selected_player_names)]
    return selected_players_gw_data


if __name__ == "__main__":
    # Gather team
    selected_player_names, left_over_money = make_initial_team_lp("2021-22")
    player_data = PlayerData("2021-22")
    selected_players_gw_data = get_selected_players_gw_one_data(player_data, selected_player_names)
    print(selected_players_gw_data)
