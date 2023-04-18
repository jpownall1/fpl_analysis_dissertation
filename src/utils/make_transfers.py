"""
make_transfers.py

This module simulates player transfers in a Fantasy Premier League (FPL) team.

Functions:
- transfer_player_random(): Randomly transfers a player based on a condition.
- transfer_player(): Transfers a player based on the highest positive delta predicted points.
- find_highest_positive_delta_predicted_points(): Finds the highest positive delta predicted points.
- filter_for_fpl_conditions(): Filters players based on FPL conditions.
- display_transfer(): Displays transfer details for console output.
"""

from src.analysis.pick_team_lp import *

# set the max_columns option to None
pd.set_option('display.max_columns', None)



def transfer_player_random(condition, all_players_df, players_df, gameweek, display_changes):
    """
    Randomly transfers a player from the `players_df` dataframe that does not meet the given `condition`, and replaces
    them with a player from the `all_players_df` dataframe that meets the `condition`. Returns the updated `players_df`.

    Args:
        condition (str): The condition that the player being added to the `players_df` dataframe must meet.
        all_players_df (pd.DataFrame): The dataframe containing all the players.
        players_df (pd.DataFrame): The dataframe containing the players already selected.
        gameweek (int): The gameweek in which the transfer takes place.
        display_changes (bool): If True, displays the console output. If False, the function does nothing.
    Returns:
        pd.DataFrame: The updated dataframe containing the players already selected.
    """
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


def transfer_player(all_players_df, players_df, display_changes, gameweek, left_over_budget):
    """
    Transfers the player with the highest positive delta predicted points, if any, from the `players_df` dataframe to
    the `all_players_df` dataframe and retrieves the player that it has the delta value with, and returns the updated
    `players_df`, the updated `left_over_budget`, the value of
    the highest positive delta predicted points, the name of the player transferred out, the name of the player
    transferred in, and the actual change in points achieved by the transfer.

    Args:
        all_players_df (pd.DataFrame): The dataframe containing all the players.
        players_df (pd.DataFrame): The dataframe containing the players already selected.
        display_changes (bool): If True, displays the console output. If False, the function does nothing.
        gameweek (int): The gameweek in which the transfer takes place.
        left_over_budget (float): The remaining budget after the transfers made so far.
    Returns:
        Tuple[pd.DataFrame, float, float, Union[str, None], Union[str, None], int]: A tuple containing the following:
            players_df (pd.DataFrame): The updated dataframe containing the players already selected.
            left_over_budget (float): The updated remaining budget after the transfers made so far.
            delta_value (float): The value of the highest positive delta predicted points.
            out_name: The name of the player transferred out. None if no such player is found.
            in_name: The name of the player transferred in. None if no such player is found.
            change_in_actual_points (int): The actual change in points achieved by the transfer.
    """

    delta_predicted_points = find_highest_positive_delta_predicted_points(players_df, all_players_df,
                                                                          left_over_budget)
    player_to_transfer_out = delta_predicted_points[0]
    player_to_transfer_in = delta_predicted_points[1]
    left_over_budget = delta_predicted_points[2]
    delta_value = delta_predicted_points[3]
    change_in_actual_points = delta_predicted_points[4]

    # If none were found, make no changes
    if player_to_transfer_out is None:
        return players_df, left_over_budget, delta_value, player_to_transfer_out, player_to_transfer_in, 0

    # Find the index of the player_transfer_out in the players_df
    transfer_out_index = players_df[players_df['name'] == player_to_transfer_out['name'].values[0]].index[0]

    # Drop the player_transfer_out from players_df
    players_df = players_df.drop(transfer_out_index).reset_index(drop=True)

    # Add the player_transfer_in to players_df
    players_df = pd.concat([players_df, player_to_transfer_in], ignore_index=True)

    display_transfer(left_over_budget, player_to_transfer_in, player_to_transfer_out, gameweek, delta_value,
                     display_changes)

    out_name = player_to_transfer_out['name'].values[0]
    in_name = player_to_transfer_in['name'].values[0]

    return players_df, left_over_budget, delta_value, out_name, in_name, change_in_actual_points


def find_highest_positive_delta_predicted_points(players_df, all_players_df, left_over_budget):
    """
        Finds the player with the highest positive delta predicted points among the players in the `players_df`
        dataframe, and returns the player selected from the transfer market, the updated `left_over_budget`, the value
        of the highest positive delta predicted points, and the actual points change.

    Args:
        players_df (pd.DataFrame): The dataframe containing the players already selected.
        all_players_df (pd.DataFrame): The dataframe containing all the players.
        left_over_budget (float): The remaining budget after the transfers made so far.
    Returns:
        Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], float, float, int]: A tuple containing the following:
            highest_positive_delta_pp_player (Optional[pd.DataFrame]): The player with the highest positive delta
                                                                       predicted points, selected from the `players_df`
                                                                       dataframe. None if no such player is found.
            transfer_market_player (Optional[pd.DataFrame]): The player selected from the transfer market. None if no
                                                             such player is found.
            left_over_budget (float): The remaining budget after choosing the player with the highest positive delta.
            highest_positive_delta_value (float): The value of the highest positive delta predicted points. Zero if no
                                                  such player is found.
            actual_points_change (int): The actual change in points achieved by the transfer.
    """
    highest_positive_delta_pp_player = None
    highest_positive_delta_value = float('-inf')
    transfer_market_player = None
    actual_points_change = 0

    # Get the list of player names from players_df
    players_df_names = players_df['name'].tolist()

    # Iterate through each player in the 15-player DataFrame
    for index, player in players_df.iterrows():
        player_value = player['value'] + left_over_budget
        player_gameweek = player['GW']
        player_position = player['position']

        filtered_players = filter_for_fpl_conditions(all_players_df, players_df, players_df_names, player_value,
                                                     player_gameweek, player_position)

        # Find the highest predicted points among the filtered players
        highest_predicted_points = filtered_players['predicted_points'].max()

        # Calculate delta_predicted_points for the current player
        delta_predicted_points = highest_predicted_points - player['predicted_points']

        # Update the highest_positive_delta_pp_player and the transfer_market_player if needed
        if delta_predicted_points > highest_positive_delta_value and delta_predicted_points > 3:
            highest_positive_delta_value = delta_predicted_points
            highest_positive_delta_pp_player = players_df.loc[[index]]
            transfer_market_player = filtered_players.loc[[filtered_players['predicted_points'].idxmax()]]

    if highest_positive_delta_pp_player is not None:
        # Update left_over_budget after choosing the player with the highest positive delta
        left_over_budget += highest_positive_delta_pp_player['value'].values[0] - \
                            transfer_market_player['value'].values[0]
        actual_points_change = transfer_market_player['total_points'].values[0] - highest_positive_delta_pp_player['total_points'].values[0]
    else:
        highest_positive_delta_value = 0

    return highest_positive_delta_pp_player, transfer_market_player, left_over_budget, highest_positive_delta_value, actual_points_change



def filter_for_fpl_conditions(all_players_df, players_df, players_df_names, player_value, player_gameweek, player_position):
    """
    Filters the all_players_df dataframe based on the given conditions and returns the filtered dataframe.

    Args:
        all_players_df (pd.DataFrame): The dataframe containing all the players.
        players_df (pd.DataFrame): The dataframe containing the players already selected.
        players_df_names (list): The list of names of the players already selected.
        player_value (float): The maximum value of the player to be selected.
        player_gameweek (int): The gameweek in which the player will play.
        player_position (str): The position of the player to be selected.
    Returns:
        pd.DataFrame: The filtered dataframe containing the players that satisfy the given conditions.
    """
    # Filter all_players_df based on the player's value (including left_over_budget), the next gameweek, and position
    filtered_players = all_players_df[(all_players_df['value'] <= player_value) &
                                  (all_players_df['GW'] == player_gameweek) &
                                  (all_players_df['position'] == player_position) &
                                  (~all_players_df['name'].isin(players_df_names))]

    # Filter out players from a team with already 3 players selected
    team_counts = players_df['team'].value_counts()
    for team in team_counts.index:
        if team_counts[team] == 3:
            filtered_players = filtered_players[filtered_players['team'] != team]

    return filtered_players


def display_transfer(left_over_budget, player_to_add, player_to_remove, gameweek, delta_value, display_changes):
    """
    Prints helpful console output for a player transfer.

    Args:
        left_over_budget (float): The remaining budget after the transfer.
        player_to_add (str): The name of the player being transferred in.
        player_to_remove (str): The name of the player being transferred out.
        gameweek (int): The gameweek in which the transfer takes place.
        delta_value (int): The maximum change in points that the transferred players can achieve.
        display_changes (bool): If True, displays the console output. If False, the function does nothing.
    Returns:
        None: This function doesn't return anything.
    """
    if display_changes:
        # helpful console output for when the changes make place
        print(f"---------------------- Gameweek:{gameweek} ----------------------")
        print("PLAYER TRANSFERRED OUT:")
        print(player_to_remove)
        print("PLAYER TRANSFERRED IN:")
        print(player_to_add)
        print("BUDGET:")
        print(left_over_budget)
        print("MAX CHANGE IN POINTS:")
        print(delta_value)
