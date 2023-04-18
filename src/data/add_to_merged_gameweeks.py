"""
add_to_merged_gameweeks.py
This module enriches merged gameweeks data for fantasy football players from different seasons by adding various
attributes such as team, position, and recent statistics. The seasons considered are from 2016-17 to 2021-22.

Functions
add_team_to_gameweeks():
Adds the team name to each player's gameweek record for all seasons.

add_position_to_gameweeks():
Adds the position of each player to their gameweek record for all seasons.

add_won_game_to_gameweeks():
Adds a binary variable (1 for win, 0 for loss/draw) to each player's gameweek record for all seasons.

add_recent_stats(column_name: str):
Adds recent statistics for a given column (e.g. total_points, bps, minutes) for each player in all seasons.

select_cols():
Selects a list of relevant columns for further analysis.

find_errors_in_gw(season: str):
Compares the length of the original and enriched gameweek data for a given season and raises an error
if the lengths are not equal.

add_id_to_player_name():
Adds the player's ID to their name for season 2021-22. This is needed for duplicate names (e.g. Ben Davies).

Usage
To enrich the gameweek data, simply call the functions at the end of the script.

Finally, run the script to process the data.
"""


import pandas as pd

seasons = ["2016-17", "2017-18", "2018-19", "2019-20", "2020-21", "2021-22"]


def add_team_to_gameweeks():
    for season in seasons:
        gw_file = '../../data/' + season + "/gws/merged_gw2.csv"
        gameweeks_df = pd.read_csv(gw_file, encoding="utf-8-sig")

        if 'team' not in gameweeks_df.columns:
            file = '../../data/' + season + "/cleaned_players.csv"
            clean_df = pd.read_csv(file, encoding="utf-8-sig")
            # this is due to name column changing from name to name with player id
            if season in ["2016-17", "2017-18"]:
                clean_df['name'] = clean_df.apply(lambda row: row["first_name"] + "_" + row["second_name"], axis=1)
            else:
                idlist_file = '../../data/' + season + '/player_idlist.csv'
                id_df = pd.read_csv(idlist_file, encoding="utf-8-sig")
                clean_df = pd.merge(clean_df, id_df, on=["first_name", "second_name"], how="left")
                clean_df['name'] = clean_df.apply(lambda row: row['first_name'] + '_' + row['second_name'] +
                                                              '_' + str(row['id']), axis=1)
            clean_df.rename(columns={'team_name': 'team'}, inplace=True)
            # clean_df = clean_df.rename({'team_name': 'team'})
            clean_df = clean_df[['name', 'team']]
            clean_df = pd.merge(gameweeks_df, clean_df, on=["name"], how="left")
            find_errors_in_gw(season)
            clean_df.to_csv(gw_file, encoding="utf-8-sig", index=False)
            print(f"Team added for season {season}")
        else:
            print(f"Team already in data for season {season}")


def add_position_to_gameweeks():
    for season in seasons:
        gw_file = '../../data/' + season + "/gws/merged_gw2.csv"
        gameweeks_df = pd.read_csv(gw_file, encoding="utf-8-sig")

        file = '../../data/' + season + "/cleaned_players.csv"
        clean_df = pd.read_csv(file, encoding="utf-8-sig")

        if 'position' not in gameweeks_df.columns:

            # this is due to name column changing from name to name with player id
            if season in ["2016-17", "2017-18"]:
                clean_df['name'] = clean_df.apply(lambda row: row["first_name"] + "_" + row["second_name"], axis=1)
            else:
                idlist_file = '../../data/' + season + '/player_idlist.csv'
                id_df = pd.read_csv(idlist_file, encoding="utf-8-sig")
                clean_df = pd.merge(clean_df, id_df, on=["first_name", "second_name"], how="left")
                clean_df['name'] = clean_df.apply(lambda row: row['first_name'] + '_' + row['second_name'] +
                                                              '_' + str(row['id']), axis=1)

            clean_df = clean_df[['name', 'position', 'team_name']]
            clean_df.rename(columns={'team_name': 'team'}, inplace=True)
            clean_df = pd.merge(gameweeks_df, clean_df, on=["name", "team"], how="left")
            find_errors_in_gw(season)
            clean_df.to_csv(gw_file, encoding="utf-8-sig", index=False)
            print(f"Position added for season {season}")
        else:
            print(f"Position already in data for season {season}")


def add_won_game_to_gameweeks():
    for season in seasons:
        gw_file = '../../data/' + season + "/gws/merged_gw2.csv"
        gameweeks_df = pd.read_csv(gw_file, encoding="utf-8-sig")

        if 'won_game' not in gameweeks_df.columns:

            def calculate_won_game(row):
                if row['team_h_score'] > row['team_a_score']:
                    if row['was_home']:
                        return 1
                    else:
                        return 0
                if row['team_h_score'] < row['team_a_score']:
                    if row['was_home']:
                        return 0
                    else:
                        return 1
                return 0

            gameweeks_df["won_game"] = gameweeks_df.apply(lambda row: calculate_won_game(row), axis=1)
            gameweeks_df.to_csv(gw_file, encoding="utf-8-sig", index=False)

            print(f"Won game added for season {season}")
        else:
            print(f"Won game already in data for season {season}")


def add_recent_stats(column_name):
    for season in seasons:
        gw_file = '../../data/' + season + "/gws/merged_gw2.csv"
        gameweeks_df = pd.read_csv(gw_file, encoding="utf-8-sig")

        if ('recent_' + column_name) not in gameweeks_df.columns:
            # gets the list of gameweek values
            gameweeks = sorted(gameweeks_df['GW'].unique())

            # initialise dataframe to contain recent stats for players to add to merged gameweeks
            to_merge_df_list = []

            # add first recent stats which is 0 at the start of the season
            first_to_merge_df = gameweeks_df.loc[gameweeks_df['GW'] == 1]
            first_to_merge_df = first_to_merge_df[['name', 'GW']]
            first_to_merge_df['recent_' + column_name] = 0
            to_merge_df_list.append(first_to_merge_df)

            # initialise gameweek subsets with subsets of length <5
            gameweek_subsets = [[1], [1, 2], [1, 2, 3], [1, 2, 3, 4]]
            # get gameweek subsets of 5 all the way to the end for getting parameters for gameweeks 5-final
            for i in range(0, len(gameweeks) - 5, 1):
                gameweek_subsets.append(gameweeks[i:i + 5])
            for subset in gameweek_subsets:
                subset_df = gameweeks_df[gameweeks_df['GW'].isin(subset)]
                df_totals = subset_df.groupby('name')[column_name].sum().to_frame(name='recent_' + column_name)
                df_totals = df_totals.reset_index()
                # have to do it this way for the gameweek value inconsistency, to put it onto the next gw
                df_totals["GW"] = gameweeks[gameweeks.index(subset[len(subset) - 1]) + 1]
                # df_totals["GW"] = subset[len(subset)-1]

                to_merge_df_list.append(df_totals)

            to_merge_df = pd.concat(to_merge_df_list)
            gameweeks_df = pd.merge(gameweeks_df, to_merge_df, on=["name", "GW"], how="left")
            # print(gameweeks_df[['name', 'GW', column_name, 'recent_' + column_name]])

            # save new merged_gw dataframe
            find_errors_in_gw(season)
            gameweeks_df.to_csv(gw_file, encoding="utf-8-sig", index=False)

            print('recent_' + column_name + f" added for season {season}")
        else:
            print('recent_' + column_name + f" already in data for season {season}")


def select_cols():
    cols = ['opponent_team', 'assists', 'threat', 'selected', 'bonus', 'ict_index', 'fixture', 'red_cards', 'was_home',
            'bps', 'round', 'penalties_missed', 'minutes', 'team', 'name', 'transfers_balance', 'value', 'team_a_score',
            'clean_sheets', 'GW', 'transfers_in', 'transfers_out', 'element', 'penalties_saved', 'goals_scored',
            'yellow_cards', 'influence', 'total_points', 'creativity', 'position', 'goals_conceded', 'saves',
            'own_goals', 'kickoff_time', 'team_h_score']


def find_errors_in_gw(season):
    print(f"----------------------------------------- For season {season}: -----------------------------------------")

    gw_file = '../../data/' + season + "/gws/merged_gw.csv"
    unaltered_gameweeks_df = pd.read_csv(gw_file, encoding="utf-8-sig")
    gw_file = '../../data/' + season + "/gws/merged_gw2.csv"
    gameweeks_df = pd.read_csv(gw_file, encoding="utf-8-sig")

    if len(unaltered_gameweeks_df) != len(gameweeks_df):
        print(f"--------------------- Checking length of files: ---------------------")
        # checks if anyone's name occurs more than the original amount of times
        unaltered_name_counts = unaltered_gameweeks_df['name'].value_counts()
        name_counts = gameweeks_df['name'].value_counts()
        difference = name_counts - unaltered_name_counts
        for name, count in difference.items():
            if count != 0:
                print(f"{name} has occured {count} more times in the altered dataframe")
        raise ValueError(f"""Gameweek files are not equal length
        Unaltered file has {len(unaltered_gameweeks_df)} entries
        New file has {len(gameweeks_df)} entries""")
    else:
        print("Gameweek files are equal length")


def add_id_to_player_name():
    season = "2021-22"
    gw_file = '../../data/' + season + "/gws/merged_gw2.csv"
    gameweeks_df = pd.read_csv(gw_file, encoding="utf-8-sig")
    gameweeks_df["name"] = gameweeks_df["name"] + "_" + gameweeks_df["element"].astype(str)
    # save new merged_gw dataframe
    find_errors_in_gw(season)
    gameweeks_df.to_csv(gw_file, encoding="utf-8-sig", index=False)

    print(f"Player id added to name for season {season}")


# do not uncomment unless starting from scratch enriching data. Needed this for duplicate Ben Davies
# add_id_to_player_name()

add_team_to_gameweeks()
add_position_to_gameweeks()
add_won_game_to_gameweeks()
add_recent_stats("total_points")
add_recent_stats("bps")
add_recent_stats("minutes")
add_recent_stats("goals_scored")
add_recent_stats("goals_conceded")
add_recent_stats("assists")
add_recent_stats("clean_sheets")
add_recent_stats("saves")
add_recent_stats("yellow_cards")
add_recent_stats("red_cards")
add_recent_stats("creativity")
add_recent_stats("won_game")

# tackles not recorded for seasons 2019-20 onward
# add_recent_stats("tackles")
# not sure if these are relevant
# add_recent_stats("transfers_in")
# add_recent_stats("transfers_out")

print()
print("Enriching data complete.")
