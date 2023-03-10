import numpy as np

from notebooks.make_transfers import *
from src.data.player_data import PlayerData
import pandas as pd
import pickle
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import freeze_support

pd.options.mode.chained_assignment = None  # default='warn'


def evaluate_variables_performance(season, position, iterations):
    # define player data object to obtain player data
    player_data = PlayerData(season)

    parameters = ["no_transfers", "transfers_on_was_home", "transfers_on_was_away",
                  "transfers_on_higher_recent_total_points",
                  "transfers_on_higher_recent_goals_scored", "transfers_on_higher_recent_yellow_cards",
                  "transfers_on_lower_recent_yellow_cards", "transfers_on_higher_recent_red_cards",
                  "transfers_on_lower_recent_red_cards", "transfers_on_higher_recent_assists",
                  "transfers_on_higher_recent_clean_sheets",
                  "transfers_on_higher_recent_saves", "transfers_on_higher_recent_minutes",
                  "transfers_on_higher_recent_bps",
                  "transfers_on_higher_recent_goals_conceded", "transfers_on_lower_recent_goals_conceded",
                  "transfers_on_higher_recent_creativity", "transfers_on_higher_recent_won_games"]

    points_track_dict = {param: np.zeros(38) for param in parameters}

    for iteration in range(iterations):
        random_players_df = player_data.select_random_players_from_gw_one(5, position)
        points_track_dict["no_transfers"] += calculate_teams_performance(player_data, random_players_df, position,
                                                                         False)
        points_track_dict["transfers_on_higher_recent_total_points"] += calculate_teams_performance(player_data,
                                                                                                    random_players_df,
                                                                                                    position, True,
                                                                                                    "recent_total_points",
                                                                                                    ">", "lowest")
        points_track_dict["transfers_on_higher_recent_minutes"] += calculate_teams_performance(player_data,
                                                                                               random_players_df,
                                                                                               position, True,
                                                                                               "recent_minutes", ">",
                                                                                               "lowest")
        points_track_dict["transfers_on_was_home"] += calculate_teams_performance(player_data, random_players_df,
                                                                                  position,
                                                                                  True, "was_home", "==",
                                                                                  "True")
        points_track_dict["transfers_on_was_away"] += calculate_teams_performance(player_data, random_players_df,
                                                                                  position,
                                                                                  True, "was_home", "==",
                                                                                  "False")
        points_track_dict["transfers_on_higher_recent_goals_scored"] += calculate_teams_performance(player_data,
                                                                                                    random_players_df,
                                                                                                    position, True,
                                                                                                    "recent_goals_scored",
                                                                                                    ">", "lowest")
        points_track_dict["transfers_on_higher_recent_yellow_cards"] += calculate_teams_performance(player_data,
                                                                                                    random_players_df,
                                                                                                    position, True,
                                                                                                    "recent_yellow_cards",
                                                                                                    ">", "lowest")
        points_track_dict["transfers_on_lower_recent_yellow_cards"] += calculate_teams_performance(player_data,
                                                                                                   random_players_df,
                                                                                                   position, True,
                                                                                                   "recent_yellow_cards",
                                                                                                   "<", "highest")
        points_track_dict["transfers_on_higher_recent_red_cards"] += calculate_teams_performance(player_data,
                                                                                                 random_players_df,
                                                                                                 position,
                                                                                                 True,
                                                                                                 "recent_red_cards",
                                                                                                 ">",
                                                                                                 "lowest")
        points_track_dict["transfers_on_lower_recent_red_cards"] += calculate_teams_performance(player_data,
                                                                                                random_players_df,
                                                                                                position,
                                                                                                True,
                                                                                                "recent_red_cards", "<",
                                                                                                "highest")
        points_track_dict["transfers_on_higher_recent_assists"] += calculate_teams_performance(player_data,
                                                                                               random_players_df,
                                                                                               position, True,
                                                                                               "recent_assists", ">",
                                                                                               "lowest")
        points_track_dict["transfers_on_higher_recent_clean_sheets"] += calculate_teams_performance(player_data,
                                                                                                    random_players_df,
                                                                                                    position, True,
                                                                                                    "recent_clean_sheets",
                                                                                                    ">", "lowest")
        points_track_dict["transfers_on_higher_recent_saves"] += calculate_teams_performance(player_data,
                                                                                             random_players_df,
                                                                                             position, True,
                                                                                             "recent_saves", ">",
                                                                                             "lowest")
        points_track_dict["transfers_on_higher_recent_bps"] += calculate_teams_performance(player_data,
                                                                                           random_players_df,
                                                                                           position, True,
                                                                                           "recent_bps", ">", "lowest")
        points_track_dict["transfers_on_higher_recent_goals_conceded"] += calculate_teams_performance(player_data,
                                                                                                      random_players_df,
                                                                                                      position, True,
                                                                                                      "recent_goals_conceded",
                                                                                                      ">", "lowest")
        points_track_dict["transfers_on_lower_recent_goals_conceded"] += calculate_teams_performance(player_data,
                                                                                                     random_players_df,
                                                                                                     position, True,
                                                                                                     "recent_goals_conceded",
                                                                                                     "<", "highest")
        points_track_dict["transfers_on_higher_recent_creativity"] += calculate_teams_performance(player_data,
                                                                                                  random_players_df,
                                                                                                  position, True,
                                                                                                  "recent_creativity",
                                                                                                  ">", "lowest")
        points_track_dict["transfers_on_higher_recent_won_games"] += calculate_teams_performance(player_data,
                                                                                                 random_players_df,
                                                                                                 position, True,
                                                                                                 "recent_won_game",
                                                                                                 ">", "lowest")

        print(f"Iteration {iteration + 1} complete for {position} {season}.")

    # change arrays to show average points per game week with transfers
    for key in points_track_dict.keys():
        points_track_dict[key] = points_track_dict[key] / iterations

    print(f"Completed all iterations for position {position} for season {season}")
    return points_track_dict


def get_average_dict(dict_of_dicts, position):
    # define the seasons as a constant list
    seasons = ["2016-17", "2017-18", "2018-19", "2019-20"]

    # create a new dictionary to store the average values
    avg_dict = {}

    # loop over the seasons
    for season in seasons:
        # get the stats for the given position and season
        stats = dict_of_dicts[f"{position}_{season}"]

        # loop over the stats
        for key, value in stats.items():
            # set the initial value of a key to zero if it doesn't exist
            avg_dict.setdefault(key, np.zeros(38))
            # add the value to the key in the avg_dict
            avg_dict[key] += value

    # compute the average value of each key using list comprehension
    avg_dict = {key: value / len(seasons) for key, value in avg_dict.items()}

    # return the average dictionary
    return avg_dict


def get_ordered_top_params_tuples(dict_of_lists, position, season):
    # Create a list of tuples containing the key and the last value of each list in the dictionary.
    list_of_tuples = [(k, v[-1]) for k, v in dict_of_lists[f"{position}_{season}"].items()]
    # Sort the list of tuples based on the last value of each list in descending order.
    sorted_list = sorted(list_of_tuples, key=lambda x: x[1], reverse=True)
    # Extract the keys from the sorted list.
    descending_keys = [t[0] for t in sorted_list]
    # Turn keys into a tuple with their position in the rankings
    ranked_keys = [(index + 1, t[0], t[1]) for index, t in enumerate(sorted_list)]
    # Save ranked keys as the top params for that position
    return ranked_keys


def get_results_dict(iterations):
    # allows use of multiple processes to run the code concurrently
    with ProcessPoolExecutor() as executor:
        results = {
            # results for 2016-17
            "gk_2016-17": executor.submit(evaluate_variables_performance, "2016-17", "GK", iterations),
            "def_2016-17": executor.submit(evaluate_variables_performance, "2016-17", "DEF", iterations),
            "mid_2016-17": executor.submit(evaluate_variables_performance, "2016-17", "MID", iterations),
            "fwd_2016-17": executor.submit(evaluate_variables_performance, "2016-17", "FWD", iterations),
            # results for 2017-18
            "gk_2017-18": executor.submit(evaluate_variables_performance, "2017-18", "GK", iterations),
            "def_2017-18": executor.submit(evaluate_variables_performance, "2017-18", "DEF", iterations),
            "mid_2017-18": executor.submit(evaluate_variables_performance, "2017-18", "MID", iterations),
            "fwd_2017-18": executor.submit(evaluate_variables_performance, "2017-18", "FWD", iterations),
            # results for 2018-19
            "gk_2018-19": executor.submit(evaluate_variables_performance, "2018-19", "GK", iterations),
            "def_2018-19": executor.submit(evaluate_variables_performance, "2018-19", "DEF", iterations),
            "mid_2018-19": executor.submit(evaluate_variables_performance, "2018-19", "MID", iterations),
            "fwd_2018-19": executor.submit(evaluate_variables_performance, "2018-19", "FWD", iterations),
            # results for 2019-20
            "gk_2019-20": executor.submit(evaluate_variables_performance, "2019-20", "GK", iterations),
            "def_2019-20": executor.submit(evaluate_variables_performance, "2019-20", "DEF", iterations),
            "mid_2019-20": executor.submit(evaluate_variables_performance, "2019-20", "MID", iterations),
            "fwd_2019-20": executor.submit(evaluate_variables_performance, "2019-20", "FWD", iterations),
            # results for 2020-21
            "gk_2020-21": executor.submit(evaluate_variables_performance, "2020-21", "GK", iterations),
            "def_2020-21": executor.submit(evaluate_variables_performance, "2020-21", "DEF", iterations),
            "mid_2020-21": executor.submit(evaluate_variables_performance, "2020-21", "MID", iterations),
            "fwd_2020-21": executor.submit(evaluate_variables_performance, "2020-21", "FWD", iterations)}

    # the submit function returns a Future object that you can use to obtain the result of the function call when it's
    # done. the result() method gets the result of the Future object .
    results_dict = {key: value.result() for key, value in results.items()}

    # get average points across all seasons for each param
    results_dict["gk_avg"] = get_average_dict(results_dict, "gk")
    results_dict["def_avg"] = get_average_dict(results_dict, "def")
    results_dict["mid_avg"] = get_average_dict(results_dict, "mid")
    results_dict["fwd_avg"] = get_average_dict(results_dict, "fwd")

    # get top params for each position
    for pos in ["gk", "def", "mid", "fwd"]:
        for season in ["2016-17", "2017-18", "2018-19", "2019-20", "2020-21", "avg"]:
            results_dict[f"{pos}_{season}_ranked_params"] = get_ordered_top_params_tuples(results_dict, pos, season)

    print("Results obtained.")

    return results_dict


if __name__ == '__main__':
    freeze_support()

    # get results
    result_dict = get_results_dict(1000)

    # save results as pickle file, so I don't need to run this file over and over as it takes a very long time.
    # wb means with byte for faster access
    print("Saving to pickle file")
    pickle_out = open("results_dict.pickle", "wb")
    pickle.dump(result_dict, pickle_out)
    pickle_out.close()
    print("Pickle file saved as 'results_dict.pickle'")
