import numpy as np

from src.data.player_data import PlayerData
from IPython.display import display
import pandas as pd
import pickle
from concurrent.futures import ProcessPoolExecutor

pd.options.mode.chained_assignment = None  # default='warn'


def calculate_players_total_points(players_df):
    total_points = players_df['total_points'].sum()
    return total_points


def calculate_teams_performance(player_data: PlayerData, initial_players_df, position, subs, parameter="", operator="",
                                value="", display_changes=False):
    if subs & (not operator or not parameter or not value):
        raise ValueError("If making subs, specify a parameter, operator and value")

    # get initial number of players for error checking
    num_players = initial_players_df.shape[0]

    # define player data object to obtain player data
    players_df = initial_players_df[['name', 'total_points', 'position', 'GW']]
    if subs:
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
    gameweeks = sorted(player_data.get_all_players_curr_season_merged_gw_stats()['GW'].nunique())
    for gameweek in gameweeks:
        # if there is a duplicate of a player (as sometimes a player has to play twice in a game week as a result
        # of a missed game) then keep the final one for this iteration
        players_df = players_df.drop_duplicates(subset=['name'], keep='last', ignore_index=True)

        # make sure there are the right amount of players each iteration
        if num_players != players_df.shape[0]:
            raise ValueError(f"Number of players has been changed from to {num_players} to {players_df.shape[0]}")

        # obtain a dataframe of all players for that gameweek
        if subs:
            all_players_df = player_data.get_all_players_curr_season_gw_stats(gameweek)[['name', 'total_points',
                                                                                         'position', 'GW', parameter]]
        else:
            all_players_df = player_data.get_all_players_curr_season_gw_stats(gameweek)[['name', 'total_points',
                                                                                         'position', 'GW']]

        # select only players of the position in question
        all_players_df = all_players_df[all_players_df.eval(f"position == '{position}'")]

        # get a list of the names already in the df
        players_names_list = players_df["name"].values

        # update current players who feature in that gameweek with their new gameweek stats
        players_in_gw_df = all_players_df[all_players_df['name'].isin(players_names_list)]

        # for players who dont feature in that gameweek, update prev stats and set points to 0
        players_in_gw_names = players_in_gw_df["name"].values
        players_not_in_gw_df = players_df[~players_df['name'].isin(players_in_gw_names)]
        players_not_in_gw_df["total_points"] = 0

        # add these back together
        players_df.update(players_in_gw_df)
        players_df = players_df.append(players_not_in_gw_df)

        # remove players already in players df from all players
        all_players_df = all_players_df[~all_players_df['name'].isin(players_names_list)]

        # find a player who does not meet condition, if there is one remove and add a player from all players who does
        if subs:
            if parameter != "was_home":
                if value == "highest":
                    value = players_df[parameter].max()
                elif value == "lowest":
                    value = players_df[parameter].min()
            condition = parameter + operator + str(value)
            players_not_meeting_condition = players_df[~players_df.eval(condition)]
            if not players_not_meeting_condition.empty:
                players_meeting_condition = all_players_df[all_players_df.eval(condition)]
                if not players_meeting_condition.empty:
                    # remove a player from the dataframe of players who do not meet the condition
                    player_to_remove = players_not_meeting_condition.sample(1)
                    players_df = pd.concat([players_df, player_to_remove, player_to_remove]).drop_duplicates(keep=False)
                    # add a player from the pool of players available to be transferred who meet the condition
                    player_to_add = players_meeting_condition.sample(1)
                    players_df = pd.concat([players_df, player_to_add])
                    if display_changes:
                        # helpful console output for when the changes make place
                        print(f"---------------------- Gameweek:{gameweek} ----------------------")
                        print("PLAYER TRANSFERRED OUT:")
                        display(player_to_remove)
                        print("PLAYER TRANSFERRED IN:")
                        display(player_to_add)

        points_track.append(calculate_players_total_points(players_df))

    if display_changes:
        # helpful console output for final team display
        print("--------------------------------- FINAL TEAM ---------------------------------")
        display(players_df)

    # error check
    if players_df.drop_duplicates(subset=['name'], keep='last').shape[0] != initial_players_df.shape[0]:
        raise ValueError(f"""Final team does not have correct amount of players. Something has gone wrong.
                         {display(players_df)}""")

    # alter points track to show accumulation of points
    for i in range(1, len(points_track)):
        points_track[i] = points_track[i - 1] + points_track[i]

    return np.asarray(points_track)


def evaluate_teams_performance(season, position, iterations):
    # define player data object to obtain player data
    player_data = PlayerData(season)

    points_track_dict = {
        "no_subs": np.zeros(39),
        "subs_on_was_home": np.zeros(39),
        "subs_on_was_away": np.zeros(39),
        "subs_on_higher_recent_total_points": np.zeros(39),
        "subs_on_higher_recent_goals_scored": np.zeros(39),
        "subs_on_higher_recent_yellow_cards": np.zeros(39),
        "subs_on_higher_recent_red_cards": np.zeros(39),
        "subs_on_higher_recent_assists": np.zeros(39),
        "subs_on_higher_recent_clean_sheets": np.zeros(39),
        "subs_on_higher_recent_saves": np.zeros(39),
        "subs_on_higher_recent_minutes": np.zeros(39),
        "subs_on_higher_recent_bps": np.zeros(39),
        "subs_on_higher_recent_goals_conceded": np.zeros(39),
        "subs_on_higher_recent_creativity": np.zeros(39),
        "subs_on_higher_recent_won_games": np.zeros(39)
    }

    for iteration in range(iterations):
        random_players_df = player_data.select_random_players(5, position)
        points_track_dict["no_subs"] += calculate_teams_performance(player_data, random_players_df, position, False)
        points_track_dict["subs_on_higher_recent_total_points"] += calculate_teams_performance(player_data,
                                                                                               random_players_df,
                                                                                               position, True,
                                                                                               "recent_total_points",
                                                                                               ">", "lowest")
        points_track_dict["subs_on_higher_recent_minutes"] += calculate_teams_performance(player_data,
                                                                                          random_players_df,
                                                                                          position, True,
                                                                                          "recent_minutes", ">",
                                                                                          "lowest")
        points_track_dict["subs_on_was_home"] += calculate_teams_performance(player_data, random_players_df, position,
                                                                             True, "was_home", "==",
                                                                             "True")
        points_track_dict["subs_on_was_away"] += calculate_teams_performance(player_data, random_players_df, position,
                                                                             True, "was_home", "==",
                                                                             "False")
        points_track_dict["subs_on_higher_recent_goals_scored"] += calculate_teams_performance(player_data,
                                                                                               random_players_df,
                                                                                               position, True,
                                                                                               "recent_goals_scored",
                                                                                               ">", "lowest")
        points_track_dict["subs_on_higher_recent_yellow_cards"] += calculate_teams_performance(player_data,
                                                                                               random_players_df,
                                                                                               position, True,
                                                                                               "recent_yellow_cards",
                                                                                               ">", "lowest")
        points_track_dict["subs_on_higher_recent_red_cards"] += calculate_teams_performance(player_data,
                                                                                            random_players_df, position,
                                                                                            True,
                                                                                            "recent_red_cards", ">",
                                                                                            "lowest")
        points_track_dict["subs_on_higher_recent_assists"] += calculate_teams_performance(player_data,
                                                                                          random_players_df,
                                                                                          position, True,
                                                                                          "recent_assists", ">",
                                                                                          "lowest")
        points_track_dict["subs_on_higher_recent_clean_sheets"] += calculate_teams_performance(player_data,
                                                                                               random_players_df,
                                                                                               position, True,
                                                                                               "recent_clean_sheets",
                                                                                               ">", "lowest")
        points_track_dict["subs_on_higher_recent_saves"] += calculate_teams_performance(player_data, random_players_df,
                                                                                        position, True,
                                                                                        "recent_saves", ">", "lowest")
        points_track_dict["subs_on_higher_recent_bps"] += calculate_teams_performance(player_data, random_players_df,
                                                                                      position, True,
                                                                                      "recent_bps", ">", "lowest")
        points_track_dict["subs_on_higher_recent_goals_conceded"] += calculate_teams_performance(player_data,
                                                                                                 random_players_df,
                                                                                                 position, True,
                                                                                                 "recent_goals_conceded",
                                                                                                 ">", "lowest")
        points_track_dict["subs_on_higher_recent_creativity"] += calculate_teams_performance(player_data,
                                                                                             random_players_df,
                                                                                             position, True,
                                                                                             "recent_creativity",
                                                                                             ">", "lowest")
        points_track_dict["subs_on_higher_recent_won_games"] += calculate_teams_performance(player_data,
                                                                                            random_players_df,
                                                                                            position, True,
                                                                                            "recent_won_game",
                                                                                            ">", "lowest")

        print(f"Iteration {iteration + 1} complete.")

    # change arrays to show average points per game week with subs
    for key in points_track_dict.keys():
        points_track_dict[key] = points_track_dict[key] / iterations

    print(f"Completed for position {position} and season {season}")
    return points_track_dict


def get_results_dict(iterations):
    # allows use of multiple processes to run the code concurrently
    with ProcessPoolExecutor() as executor:
        results = {
            # results for 2016-17
            "gk_2016-17": executor.submit(evaluate_teams_performance, "2016-17", "GK", iterations),
            "def_2016-17": executor.submit(evaluate_teams_performance, "2016-17", "DEF", iterations),
            "mid_2016-17": executor.submit(evaluate_teams_performance, "2016-17", "MID", iterations),
            "fwd_2016-17": executor.submit(evaluate_teams_performance, "2016-17", "FWD", iterations),
            # results for 2017-18
            "gk_2017-18": executor.submit(evaluate_teams_performance, "2017-18", "GK", iterations),
            "def_2017-18": executor.submit(evaluate_teams_performance, "2017-18", "DEF", iterations),
            "mid_2017-18": executor.submit(evaluate_teams_performance, "2017-18", "MID", iterations),
            "fwd_2017-18": executor.submit(evaluate_teams_performance, "2017-18", "FWD", iterations),
            # results for 2018-19
            "gk_2018-19": executor.submit(evaluate_teams_performance, "2018-19", "GK", iterations),
            "def_2018-19": executor.submit(evaluate_teams_performance, "2018-19", "DEF", iterations),
            "mid_2018-19": executor.submit(evaluate_teams_performance, "2018-19", "MID", iterations),
            "fwd_2018-19": executor.submit(evaluate_teams_performance, "2018-19", "FWD", iterations),
            # results for 2019-20
            "gk_2019-20": executor.submit(evaluate_teams_performance, "2019-20", "GK", iterations),
            "def_2019-20": executor.submit(evaluate_teams_performance, "2019-20", "DEF", iterations),
            "mid_2019-20": executor.submit(evaluate_teams_performance, "2019-20", "MID", iterations),
            "fwd_2019-20": executor.submit(evaluate_teams_performance, "2019-20", "FWD", iterations),
            # results for 2020-21
            "gk_2020-21": executor.submit(evaluate_teams_performance, "2020-21", "GK", iterations),
            "def_2020-21": executor.submit(evaluate_teams_performance, "2020-21", "DEF", iterations),
            "mid_2020-21": executor.submit(evaluate_teams_performance, "2020-21", "MID", iterations),
            "fwd_2020-21": executor.submit(evaluate_teams_performance, "2020-21", "FWD", iterations),
            # results for 2021-22
            "gk_2021-22": executor.submit(evaluate_teams_performance, "2021-22", "GK", iterations),
            "def_2021-22": executor.submit(evaluate_teams_performance, "2021-22", "DEF", iterations),
            "mid_2021-22": executor.submit(evaluate_teams_performance, "2021-22", "MID", iterations),
            "fwd_2021-22": executor.submit(evaluate_teams_performance, "2021-22", "FWD", iterations)}

    # the submit function returns a Future object that you can use to obtain the result of the function call when it's
    # done. the result() method gets the result of the Future object .
    return {key: value.result() for key, value in results.items()}


# get results
results_dict = get_results_dict(1000)

# save results as pickle file, so I don't need to run this file over and over as it takes a very long time.
# wb means with byte for faster access
pickle_out = open("results_dict.pickle", "wb")
pickle.dump(results_dict, pickle_out)
pickle_out.close()
