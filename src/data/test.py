import numpy as np
import pulp as pulp

from player_data import PlayerData
from src.data.season_data import SeasonData
from team_data import TeamData
from IPython.display import display
import pandas as pd


def get_historical_stats_with_curr_price(season):
    # get previous seasons player stats
    players = PlayerData(season)
    last_s_data = players.get_all_players_prev_season_stats()
    last_s_data = last_s_data[['first_name', 'second_name', 'total_points', 'minutes', 'team_name', 'position']]
    # remove players who have not played around 30 games
    last_s_data = last_s_data.drop(last_s_data[last_s_data.minutes < 90 * 30].index)

    # get current season player stats
    this_s_data = players.get_all_players_curr_season_stats()
    this_s_data = this_s_data[['first_name', 'second_name', 'initial_cost', 'team_name', 'position']]

    # merge together, this eliminates players who are newly promoted or relegated
    merged_df = pd.merge(last_s_data, this_s_data, on=["first_name", "second_name", 'team_name', 'position'])

    # find if players have changed teams?------------------------------------------------------------------------

    return merged_df


def make_initial_team_lp(season):
    # filtered dataframe
    data = get_historical_stats_with_curr_price(season)
    data['name'] = data.apply(lambda row: row['first_name'] + " " + row['second_name'], axis=1)

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
    names = [data.name[i] for i in data.index]
    teams = [data.team_name[i] for i in data.index]
    positions = [data.position[i] for i in data.index]
    prices = [data.initial_cost[i] for i in data.index]
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

    team_df = pd.DataFrame(columns=["name", "club", "position", "historical_points", "starting"])
    tot_price = 0
    for v in prob.variables():
        if v.varValue != 0:
            name = data.name[int(v.name.split("_")[1])]
            club = data.team_name[int(v.name.split("_")[1])]
            position = data.position[int(v.name.split("_")[1])]
            points = data.total_points[int(v.name.split("_")[1])]
            price = data.initial_cost[int(v.name.split("_")[1])]
            # print(name, position, club, points, price, sep=" | ")
            team_df = team_df.append({"name": name, "club": club, "position": position, "historical_points": points},
                                     ignore_index=True)
            tot_price += price

    left_over_money = BUDGET - tot_price
    return team_df, left_over_money


def select_initial_starting_11(season):
    team = make_initial_team_lp(season)[0]
    team = team.sort_values("historical_points")
    starting_df = team.head(11)
    sub_df = team.tail(4)
    num_gks_s11 = (starting_df.position == "GK").sum()
    if num_gks_s11 < 1:
        gks = team[team.position == "GK"]
        highest_points_gk = gks.head(1)
        lowest_points_player = starting_df.tail(1)
        starting_df = pd.concat([starting_df, lowest_points_player, lowest_points_player]).drop_duplicates(keep=False)
        sub_df = pd.concat([sub_df, lowest_points_player])
        starting_df = pd.concat([starting_df, highest_points_gk])
        sub_df = pd.concat([sub_df, highest_points_gk, highest_points_gk]).drop_duplicates(keep=False)
    elif num_gks_s11 > 1:
        gks = starting_df[starting_df.position == "GK"]
        lowest_points_gk = gks.tail(1)
        highest_points_sub_player = sub_df.head(1)
        starting_df = pd.concat([starting_df, lowest_points_gk, lowest_points_gk]).drop_duplicates(keep=False)
        sub_df = pd.concat([sub_df, lowest_points_gk])
        starting_df = pd.concat([starting_df, highest_points_sub_player])
        sub_df = pd.concat([sub_df, highest_points_sub_player, highest_points_sub_player]).drop_duplicates(keep=False)

    defenders_count = (starting_df.position == "DEF").sum()
    midfielders_count = (starting_df.position == "MID").sum()
    forwards_count = (starting_df.position == "FWD").sum()
    print(f"Formation is {defenders_count}-{midfielders_count}-{forwards_count}")

    return starting_df, sub_df


team = select_initial_starting_11("2019-20")
print("Starting:")
display(team[0])
print("Subs:")
display(team[1])
