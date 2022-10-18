import pandas as pd
from IPython.core.display import display

seasons = ["2016-17", "2017-18", "2018-19", "2019-20", "2020-21", "2021-22"]

def add_position_to_clean():
    for season in seasons:

        data_location = '../../data/historical_data/' + season + "/"
        clean_df = pd.read_csv(data_location + "cleaned_players.csv", encoding="ISO-8859-1")
        if 'element_type' in clean_df.columns:
            clean_df = clean_df.drop('element_type', axis=1)
        if 'position' in clean_df.columns:
            clean_df = clean_df.drop('position', axis=1)
        raw_df = pd.read_csv(data_location + "players_raw.csv", encoding = "ISO-8859-1")
        raw_df = raw_df[['first_name', 'second_name', 'element_type']]
        clean_df = pd.merge(clean_df, raw_df, on=["first_name", "second_name"])

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
        clean_df.to_csv(data_location + "cleaned_players.csv")

def add_initial_cost_to_clean():
    for season in seasons:
        data_location = '../../data/historical_data/' + season + "/"
        clean_df = pd.read_csv(data_location + "cleaned_players.csv", encoding="ISO-8859-1")
        if 'initial_cost' in clean_df.columns:
            clean_df = clean_df.drop('initial_cost', axis=1)
        raw_df = pd.read_csv(data_location + "players_raw.csv", encoding="ISO-8859-1")
        if 'now_cost' in clean_df.columns:
            raw_df = raw_df[['first_name', 'second_name', 'cost_change_start']]
        else:
            raw_df = raw_df[['first_name', 'second_name', 'now_cost', 'cost_change_start']]
        clean_df = pd.merge(clean_df, raw_df, on=["first_name", "second_name"])

        clean_df['initial_cost'] = clean_df.apply(lambda row: row['now_cost'] - row['cost_change_start'], axis=1)
        clean_df = clean_df.drop('cost_change_start', axis=1)
        clean_df.to_csv(data_location + "cleaned_players.csv")

def add_minutes_played():
    for season in seasons:
        data_location = '../../data/historical_data/' + season + "/"
        clean_df = pd.read_csv(data_location + "cleaned_players.csv", encoding="ISO-8859-1")
        if 'minutes' in clean_df.columns:
            clean_df = clean_df.drop('minutes', axis=1)
        if 'points_per_min' in clean_df.columns:
            clean_df = clean_df.drop('points_per_min', axis=1)
        raw_df = pd.read_csv(data_location + "players_raw.csv", encoding="ISO-8859-1")
        raw_df = raw_df[['first_name', 'second_name', 'minutes']]
        clean_df = pd.merge(clean_df, raw_df, on=["first_name", "second_name"])

        clean_df['points_per_min'] = clean_df.apply(lambda row: row['now_cost'] - row['cost_change_start'], axis=1)
        clean_df = clean_df.drop('cost_change_start', axis=1)
        clean_df.to_csv(data_location + "cleaned_players.csv")

def select_cols():
    for season in seasons:
        data_location = '../../data/historical_data/' + season + "/"
        clean_df = pd.read_csv(data_location + "cleaned_players.csv", encoding="ISO-8859-1")
        clean_df = (clean_df[['first_name', 'second_name', 'goals_scored', 'assists', 'total_points', 'minutes',
                              'goals_conceded', 'creativity', 'influence', 'threat', 'bonus', 'bps', 'ict_index',
                              'clean_sheets', 'red_cards', 'yellow_cards', 'selected_by_percent', 'now_cost', 'element_type',
                              'position', 'initial_cost']])
        clean_df.to_csv(data_location + "cleaned_players.csv")

add_position_to_clean()
add_initial_cost_to_clean()
select_cols()

print("done")
