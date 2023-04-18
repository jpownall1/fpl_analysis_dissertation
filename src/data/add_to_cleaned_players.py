"""
add_to_cleaned_players.py: A Python script that adds extra information to cleaned_players.csv files for each season.

This script performs the following tasks:

Adds position, initial cost, and team name columns to the cleaned players DataFrame.
Selects and orders the columns.
Adds a name column that combines first name and second name columns.
Creates a name column with player ID.

Usage:
Simply run the script with Python interpreter. No arguments are required.

Dependencies:
- pandas
- pathlib
- IPython.core.display_functions

Example:
$ python add_to_cleaned_players.py
"""

import pandas as pd
from pathlib import Path

from IPython.core.display_functions import display

seasons = ["2016-17", "2017-18", "2018-19", "2019-20", "2020-21", "2021-22"]
data_directory_location = str(Path(__file__).parent) + '/../../data/'
from pathlib import Path


def add_position_to_clean(seasons):
    for season in seasons:
        data_location = data_directory_location + season + "/"
        old_clean_df = pd.read_csv(data_location + "cleaned_players.csv", encoding="utf-8-sig")
        clean_df = pd.read_csv(data_location + "cleaned_players.csv", encoding="utf-8-sig")
        if 'element_type' in clean_df.columns:
            clean_df = clean_df.drop('element_type', axis=1)
        if 'position' in clean_df.columns:
            clean_df = clean_df.drop('position', axis=1)
        raw_df = pd.read_csv(data_location + "players_raw.csv", encoding="utf-8-sig")
        raw_df = raw_df[['first_name', 'second_name', 'element_type', 'total_points']]
        clean_df = pd.merge(clean_df, raw_df, on=["first_name", "second_name", 'total_points'], how="left")

        def convert_to_position(row):
            if row['element_type'] == 1:
                return 'GK'
            elif row['element_type'] == 2:
                return 'DEF'
            elif row['element_type'] == 3:
                return 'MID'
            elif row['element_type'] == 4:
                return 'FWD'
            else:
                return 'N/A'

        clean_df['position'] = clean_df.apply(lambda row: convert_to_position(row), axis=1)
        if len(clean_df) != len(old_clean_df): raise ValueError('Lengths not equal')
        clean_df.to_csv(data_location + "cleaned_players.csv", encoding="utf-8-sig", index=False)
        print(f"Position added for season {season}")


def add_costs_to_clean(seasons):
    for season in seasons:
        data_location = data_directory_location + season + "/"
        old_clean_df = pd.read_csv(data_location + "cleaned_players.csv", encoding="utf-8-sig")
        clean_df = pd.read_csv(data_location + "cleaned_players.csv", encoding="utf-8-sig")
        if 'initial_cost' in clean_df.columns:
            clean_df = clean_df.drop('initial_cost', axis=1)
        raw_df = pd.read_csv(data_location + "players_raw.csv", encoding="utf-8-sig")
        if 'now_cost' in clean_df.columns:
            raw_df = raw_df[['first_name', 'second_name', 'cost_change_start', 'total_points']]
        else:
            raw_df = raw_df[['first_name', 'second_name', 'now_cost', 'cost_change_start', 'total_points']]
        clean_df = pd.merge(clean_df, raw_df, on=["first_name", "second_name", 'total_points'], how="left")

        clean_df['initial_cost'] = clean_df.apply(lambda row: row['now_cost'] - row['cost_change_start'], axis=1)
        clean_df = clean_df.drop('cost_change_start', axis=1)
        if len(clean_df) != len(old_clean_df): raise ValueError('Lengths not equal')
        clean_df.to_csv(data_location + "cleaned_players.csv", encoding="utf-8-sig", index=False)
        print(f"Costs added for season {season}")


def add_team_name_to_clean(seasons):
    for season in seasons:
        data_location = data_directory_location + season + "/"
        old_clean_df = pd.read_csv(data_location + "cleaned_players.csv", encoding="utf-8-sig")
        clean_df = pd.read_csv(data_location + "cleaned_players.csv", encoding="utf-8-sig")
        if 'team_name' in clean_df.columns:
            clean_df = clean_df.drop('team_name', axis=1)
        raw_df = pd.read_csv(data_location + "players_raw.csv", encoding="utf-8-sig")
        raw_df = raw_df[['first_name', 'second_name', 'team', 'total_points']]
        teams_df = pd.read_csv(data_location + "teams.csv", encoding="utf-8-sig")
        teams_df = teams_df[['id', "short_name"]]
        teams_df.rename(columns={'id': 'team', 'short_name': 'team_name'}, inplace=True)
        raw_df = pd.merge(raw_df, teams_df, on='team', how="left")
        clean_df = pd.merge(clean_df, raw_df, on=["first_name", "second_name", 'total_points'], how="left")
        clean_df = clean_df.drop('team', axis=1)
        if len(clean_df) != len(old_clean_df): raise ValueError('Lengths not equal')
        clean_df.to_csv(data_location + "cleaned_players.csv", encoding="utf-8-sig", index=False)
        print(f"Team names added for season {season}")


def select_cols(seasons):
    for season in seasons:
        data_location = data_directory_location + season + "/"
        old_clean_df = pd.read_csv(data_location + "cleaned_players.csv", encoding="utf-8-sig")
        clean_df = pd.read_csv(data_location + "cleaned_players.csv", encoding="utf-8-sig")
        clean_df = (clean_df[['name', 'first_name', 'second_name', 'goals_scored', 'assists', 'total_points', 'minutes',
                              'goals_conceded', 'creativity', 'influence', 'threat', 'bonus', 'bps', 'ict_index',
                              'clean_sheets', 'red_cards', 'yellow_cards', 'selected_by_percent', 'now_cost',
                              'element_type', 'position', 'initial_cost', 'team_name']])
        clean_df.drop_duplicates(keep=False)
        if len(clean_df) != len(old_clean_df): raise ValueError('Lengths not equal')
        clean_df.to_csv(data_location + "cleaned_players.csv", encoding="utf-8-sig", index=False)
        print(f"Cleaned players finished for season {season}")


def add_name_column(seasons):
    for season in seasons:
        # Read the CSV files
        data_location = data_directory_location + season + "/"
        cleaned_players = pd.read_csv(data_location + "cleaned_players.csv", encoding="utf-8-sig")
        id_dict = pd.read_csv(data_location + "player_idlist.csv", encoding="utf-8-sig")
        if 'name' in cleaned_players.columns:
            print(f"Name already in columns for clean df in season {season}.")
            break

        # Strip the column names
        id_dict.columns = id_dict.columns.str.strip()

        # Create a new 'name' column in each df
        cleaned_players['name'] = cleaned_players['first_name'] + " " + cleaned_players['second_name']
        id_dict['name'] = id_dict['first_name'] + " " + id_dict['second_name']

        # Merge cleaned_players with id_dict to add the 'FPL_ID' column
        merged_players = pd.merge(cleaned_players, id_dict[['name', 'id']], on='name', how="left")

        # Fill any missing values in the 'FPL_ID' column with a default value, e.g., -1
        merged_players['id'] = merged_players['id'].fillna(-1)

        # Convert the 'FPL_ID' column to integer data type
        merged_players['id'] = merged_players['id'].astype(int)

        # Create a new 'name_with_id' column by concatenating the 'name' and 'FPL_ID' columns
        merged_players['name'] = merged_players['name'] + "_" + merged_players['id'].astype(str)

        # Save the updated DataFrame to a new CSV file
        merged_players.to_csv(data_location + "cleaned_players_with_name_id.csv", index=False, encoding="utf-8-sig")


seasons = ["2016-17", "2017-18", "2018-19", "2019-20", "2020-21", "2021-22"]
# add_position_to_clean(seasons)
# add_costs_to_clean(seasons)
# add_team_name_to_clean(seasons)
# select_cols(seasons)
add_name_column(["2021-22"])

print("done")
