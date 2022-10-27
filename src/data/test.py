import numpy as np
import pulp as pulp

from player_data import PlayerData
from src.data.season_data import SeasonData
from team_data import TeamData
from IPython.display import display
import pandas as pd


def sort_by_cpi(season):
    # get previous seasons player stats
    season = SeasonData(season)
    last_s_data = season.get_all_players_prev_season_stats()
    last_s_data = last_s_data[['first_name', 'second_name', 'total_points', 'minutes', 'team_name', 'position']]
    # remove players who have not played around 30 games
    last_s_data = last_s_data.drop(last_s_data[last_s_data.minutes < 90 * 30].index)

    # get current season player stats
    this_s_data = season.get_all_players_curr_season_stats()
    this_s_data = this_s_data[['first_name', 'second_name', 'initial_cost', 'team_name', 'position']]

    # merge together, this eliminates players who are newly promoted or relegated
    merged_df = pd.merge(last_s_data, this_s_data, on=["first_name", "second_name", 'team_name', 'position'])

    # find if players have changed teams?------------------------------------------------------------------------

    # derive points_per_mil, points_per_min and cpi
    merged_df['points_per_mil'] = np.where(merged_df['initial_cost'] != 0,
                                           merged_df['total_points'] / merged_df['initial_cost'], 0)
    merged_df['points_per_min'] = np.where(merged_df['initial_cost'] != 0,
                                           merged_df['total_points'] / merged_df['minutes'], 0)
    max_ppm = merged_df['points_per_mil'].max()
    max_ppmin = merged_df['points_per_min'].max()
    merged_df['cpi'] = merged_df.apply(lambda row: row['points_per_mil'] / max_ppm + row['points_per_min'] / max_ppmin,
                                       axis=1)
    merged_df['is_goalkeeper'] = merged_df.apply(lambda row: row['position'] == "GK", axis=1)
    merged_df['is_defender'] = merged_df.apply(lambda row: row['position'] == "DEF", axis=1)
    merged_df['is_midfielder'] = merged_df.apply(lambda row: row['position'] == "MID", axis=1)
    merged_df['is_forward'] = merged_df.apply(lambda row: row['position'] == "FWD", axis=1)

    return merged_df.sort_values(by=['cpi'], ascending=False)


def add_team_dummy(df):
    for t in df.team_name.unique():
        df['team_' + str(t)] = np.where(df.team_name == t, int(1), int(0))
    return df
def make_11_lp(season):
    cpi_df = sort_by_cpi(season)

    constraints = {
        "GK": 2,
        "DEF": 5,
        "MID": 5,
        "FWD": 3,
        "total_cost": 1000,
        "max_common_team": 3
    }
    max_cost = 1000

    fpl_problem = pulp.LpProblem('FPL', pulp.LpMaximize)

    cpi_df['full_name'] = cpi_df.apply(lambda row: row['first_name'] + " " + row['second_name'], axis=1)

    cpi_df = add_team_dummy(cpi_df)

    players = cpi_df.full_name

    # create a dictionary of pulp variables with keys from names
    x = pulp.LpVariable.dict('x_ % s', players, lowBound=0, upBound=1,
                             cat=pulp.LpInteger)

    # player score data
    player_points = dict(
        zip(cpi_df.full_name, np.array(cpi_df["total_points"])))

    # objective function
    fpl_problem += sum([player_points[i] * x[i] for i in players])

    # could get straight from dataframe...
    player_cost = dict(zip(cpi_df.full_name, cpi_df.initial_cost))
    player_position = dict(zip(cpi_df.full_name, cpi_df.position))
    player_gk = dict(zip(cpi_df.full_name, cpi_df.is_goalkeeper))
    player_def = dict(zip(cpi_df.full_name, cpi_df.is_defender))
    player_mid = dict(zip(cpi_df.full_name, cpi_df.is_midfielder))
    player_fwd = dict(zip(cpi_df.full_name, cpi_df.is_forward))

    # apply the constraints
    fpl_problem += sum([player_cost[i] * x[i] for i in players]) <= float(constraints['total_cost'])
    fpl_problem += sum([player_gk[i] * x[i] for i in players]) == constraints['GK']
    fpl_problem += sum([player_def[i] * x[i] for i in players]) == constraints['DEF']
    fpl_problem += sum([player_mid[i] * x[i] for i in players]) == constraints['MID']
    fpl_problem += sum([player_fwd[i] * x[i] for i in players]) == constraints['FWD']

    for t in cpi_df.team_name:
        player_team = dict(
            zip(cpi_df.full_name, cpi_df['team_' + str(t)]))
        fpl_problem += sum([player_team[i] * x[i] for i in players]) <= constraints['max_common_team']

    # solve the thing
    fpl_problem.solve()

    total_points = 0.
    total_cost = 0.
    optimal_squad = []
    for p in players:
        if x[p].value() != 0:
            total_points += player_points[p]
            total_cost += player_cost[p]

            optimal_squad.append({
                'name': p,
                'position': player_position[p],
                'cost': player_cost[p],
                'points': player_points[p]
            })

    solution_info = {
        'total_points': total_points,
        'total_cost': total_cost
    }

    return optimal_squad, solution_info

print(make_11_lp("2020-21"))


