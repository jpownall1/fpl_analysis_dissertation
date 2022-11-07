import pulp as pulp

from src.data.player_data import PlayerData
from IPython.display import display
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
    this_s_data = players.get_all_players_curr_season_stats()
    this_s_data = this_s_data[['first_name', 'second_name', 'initial_cost', 'team_name', 'position']]

    # merge together, this eliminates players who are newly promoted or relegated
    # merging on team_name also eliminates players who have changed teams
    merged_df = pd.merge(last_s_data, this_s_data, on=["first_name", "second_name", 'team_name', 'position'])

    # find if players have changed teams?------------------------------------------------------------------------

    return merged_df


def make_initial_team_lp(season):
    """
    Uses linear programming python module PuLP to pick the initial team for a season based on amount of points
    scored historically with position, budget and team constraints.

    params:
    season - season to pick the team for

    returns:
    team_df - a Pandas dataframe of the picked team
    left_over_money - the amount of money left over from picking the team
    """
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

    team_df = pd.DataFrame(columns=["first_name", "second_name", "club", "position", "historical_points"])
    tot_price = 0
    for v in prob.variables():
        if v.varValue != 0:
            first_name = data.first_name[int(v.name.split("_")[1])]
            second_name = data.second_name[int(v.name.split("_")[1])]
            club = data.team_name[int(v.name.split("_")[1])]
            position = data.position[int(v.name.split("_")[1])]
            points = data.total_points[int(v.name.split("_")[1])]
            price = data.initial_cost[int(v.name.split("_")[1])]
            #print(first_name, second_name, position, club, points, price, sep=" | ")
            team_df = team_df.append({"first_name": first_name, "second_name": second_name, "club": club,
                                      "position": position, "historical_points": points},
                                     ignore_index=True)
            tot_price += price

    left_over_money = BUDGET - tot_price
    return team_df, left_over_money

def switch_player_entry(entry, df_to_add, df_to_drop):
    """
    Method to switch a player from one dataframe to another with the same columns. Particulatly useful when
    switching between starting 11 and subs

    params:
    entry - Pandas DF of one player entry i.e. the player to switch
    df_to_add - the dataframe to add the player to
    df_to_drop - the dataframe to drop the player from

    returns:
    df_to_add - the dataframe with the added player
    df_to_drop - the dataframe with the dropped player
    """
    df_to_drop = pd.concat([df_to_drop, entry, entry]).drop_duplicates(keep=False)
    df_to_add = pd.concat([df_to_add, entry])

    return df_to_add, df_to_drop
def select_initial_starting_11(season):

    #gather team
    team = make_initial_team_lp(season)[0]

    #pick top 11 players who got the most points historically and add the rest to subs
    team = team.sort_values("historical_points", ascending=False)
    starting_df = team.head(11)
    sub_df = team.tail(4)

    #make sure there is 1 goalkeeper in the team
    num_gks_s11 = (starting_df.position == "GK").sum()
    if num_gks_s11 < 1:
        gks = team[team.position == "GK"]
        highest_points_gk = gks.head(1)
        lowest_points_player = starting_df.tail(1)
        #sub off lowest points player
        sub_df, starting_df = switch_player_entry(lowest_points_player, sub_df, starting_df)
        #sub on highest points keeper
        starting_df, sub_df = switch_player_entry(highest_points_gk, starting_df, sub_df)
    elif num_gks_s11 > 1:
        gks = starting_df[starting_df.position == "GK"]
        lowest_points_gk = gks.tail(1)
        highest_points_sub_player = sub_df.head(1)
        #sub off lowest points gk
        sub_df, starting_df = switch_player_entry(lowest_points_gk, sub_df, starting_df)
        #sub on highest points player
        starting_df, sub_df = switch_player_entry(highest_points_sub_player, starting_df, sub_df)

    #print formation
    defenders_count = (starting_df.position == "DEF").sum()
    midfielders_count = (starting_df.position == "MID").sum()
    forwards_count = (starting_df.position == "FWD").sum()
    print(f"Formation is {defenders_count}-{midfielders_count}-{forwards_count}")

    #drop historical_points as they are no longer needed
    starting_df = starting_df.drop('historical_points', axis=1)
    sub_df = sub_df.drop('historical_points', axis=1)

    return starting_df, sub_df


team = select_initial_starting_11("2020-21")
print("Starting:")
display(team[0])
print("Subs:")
display(team[1])
