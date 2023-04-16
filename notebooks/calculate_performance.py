import numpy as np

from notebooks.make_transfers import transfer_player_random, transfer_player
from notebooks.organise_team import organise_team
from notebooks.utils import check_team_size
from src.data.player_data import PlayerData


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
        print(players_df)

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
        print(players_df)

    # alter points track to show accumulation of points
    points_track = accumulate_points(points_track)

    return np.asarray(points_track)


def calculate_teams_performance(player_data: PlayerData, initial_players_df, variable="",
                                display_changes=False, left_over_budget=0):
    # Check if there are 15 players in the squad
    if initial_players_df.shape[0] != 15:
        print(f"The team has {initial_players_df.shape[0]} players, but the desired number of players is {15}.")

    # define player data object to obtain player data
    players_df = initial_players_df[
        ['name', 'minutes', 'kickoff_time', 'total_points', 'position', 'GW', 'value', variable]].copy()

    # helpful console output for initial team display
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
             'position', 'GW', 'value',
             variable]]

        # update stats for players in gameweek
        players_df = update_players_stats(players_df, all_players_df)

        # transfer player
        players_df, left_over_budget = transfer_player(all_players_df, players_df, display_changes, gameweek,
                                                       left_over_budget)

        # Organise team and calculate points earnt
        starting_df, subs_df = organise_team(players_df, "predicted_points")
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


def calculate_players_total_points(players_df):
    total_points = players_df['total_points'].sum()
    print(f"Total team points: {total_points}")
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


def accumulate_points(points_track):
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
