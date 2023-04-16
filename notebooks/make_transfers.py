import numpy as np
# from line_profiler_pycharm import profile

from src.data.player_data import PlayerData
from IPython.display import display
import pandas as pd
from notebooks.pick_team_lp import *
from notebooks.organise_team import select_initial_starting_11, organise_team

# set the max_columns option to None
pd.set_option('display.max_columns', None)


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


def transfer_player(all_players_df, players_df, display_changes, gameweek, left_over_budget):
    delta_predicted_points = find_highest_positive_delta_predicted_points(players_df, all_players_df,
                                                                          left_over_budget)
    player_to_transfer_out = delta_predicted_points[0]
    player_to_transfer_in = delta_predicted_points[1]
    left_over_budget = delta_predicted_points[2]
    delta_value = delta_predicted_points[3]
    # Find the index of the player_transfer_out in the players_df
    transfer_out_index = players_df[players_df['name'] == player_to_transfer_out['name'].values[0]].index[0]

    # Drop the player_transfer_out from players_df
    players_df = players_df.drop(transfer_out_index).reset_index(drop=True)

    # Add the player_transfer_in to players_df
    players_df = pd.concat([players_df, player_to_transfer_in], ignore_index=True)

    display_transfer(left_over_budget, player_to_transfer_in, player_to_transfer_out, gameweek, delta_value,
                     display_changes)

    return players_df, left_over_budget


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

    return highest_positive_delta_player, highest_predicted_points_player, left_over_budget, highest_positive_delta_value


def display_transfer(left_over_budget, player_to_add, player_to_remove, gameweek, delta_value, display_changes):
    if display_changes:
        # helpful console output for when the changes make place
        print(f"---------------------- Gameweek:{gameweek} ----------------------")
        print("PLAYER TRANSFERRED OUT:")
        display(player_to_remove)
        print("PLAYER TRANSFERRED IN:")
        display(player_to_add)
        print("BUDGET:")
        print(left_over_budget)
        print("MAX CHANGE IN POINTS:")
        print(delta_value)
