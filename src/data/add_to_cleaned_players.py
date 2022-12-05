import pandas as pd
from IPython.core.display import display

seasons = ["2016-17", "2017-18", "2018-19", "2019-20", "2020-21", "2021-22"]


def add_position_to_clean():
    for season in seasons:
        data_location = '../../data/' + season + "/"
        clean_df = pd.read_csv(data_location + "cleaned_players.csv", encoding="ISO-8859-1")
        if 'element_type' in clean_df.columns:
            clean_df = clean_df.drop('element_type', axis=1)
        if 'position' in clean_df.columns:
            clean_df = clean_df.drop('position', axis=1)
        raw_df = pd.read_csv(data_location + "players_raw.csv", encoding="ISO-8859-1")
        raw_df = raw_df[['first_name', 'second_name', 'element_type', 'total_points']]
        clean_df = pd.merge(clean_df, raw_df, on=["first_name", "second_name", 'total_points'])

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
        print(f"Position added for season {season}")


def add_costs_to_clean():
    for season in seasons:
        data_location = '../../data/' + season + "/"
        clean_df = pd.read_csv(data_location + "cleaned_players.csv", encoding="ISO-8859-1")
        if 'initial_cost' in clean_df.columns:
            clean_df = clean_df.drop('initial_cost', axis=1)
        raw_df = pd.read_csv(data_location + "players_raw.csv", encoding="ISO-8859-1")
        if 'now_cost' in clean_df.columns:
            raw_df = raw_df[['first_name', 'second_name', 'cost_change_start', 'total_points']]
        else:
            raw_df = raw_df[['first_name', 'second_name', 'now_cost', 'cost_change_start', 'total_points']]
        clean_df = pd.merge(clean_df, raw_df, on=["first_name", "second_name", 'total_points'])

        clean_df['initial_cost'] = clean_df.apply(lambda row: row['now_cost'] - row['cost_change_start'], axis=1)
        clean_df = clean_df.drop('cost_change_start', axis=1)
        clean_df.to_csv(data_location + "cleaned_players.csv")
        print(f"Costs added for season {season}")


def add_team_name_to_clean():
    for season in seasons:
        data_location = '../../data/' + season + "/"
        clean_df = pd.read_csv(data_location + "cleaned_players.csv", encoding="ISO-8859-1")
        if 'team_name' in clean_df.columns:
            clean_df = clean_df.drop('team_name', axis=1)
        raw_df = pd.read_csv(data_location + "players_raw.csv", encoding="ISO-8859-1")
        raw_df = raw_df[['first_name', 'second_name', 'team', 'total_points']]
        teams_df = pd.read_csv(data_location + "teams.csv", encoding="ISO-8859-1")
        teams_df = teams_df[['id', "short_name"]]
        teams_df.rename(columns={'id': 'team', 'short_name': 'team_name'}, inplace=True)
        raw_df = pd.merge(raw_df, teams_df, on='team')
        clean_df = pd.merge(clean_df, raw_df, on=["first_name", "second_name", 'total_points'])
        clean_df = clean_df.drop('team', axis=1)
        clean_df.to_csv(data_location + "cleaned_players.csv")
        print(f"Team names added for season {season}")


def select_cols():
    for season in seasons:
        data_location = '../../data/' + season + "/"
        clean_df = pd.read_csv(data_location + "cleaned_players.csv", encoding="ISO-8859-1")
        clean_df = (clean_df[['first_name', 'second_name', 'goals_scored', 'assists', 'total_points', 'minutes',
                              'goals_conceded', 'creativity', 'influence', 'threat', 'bonus', 'bps', 'ict_index',
                              'clean_sheets', 'red_cards', 'yellow_cards', 'selected_by_percent', 'now_cost',
                              'element_type', 'position', 'initial_cost', 'team_name']])
        clean_df.drop_duplicates(keep=False)
        clean_df.to_csv(data_location + "cleaned_players.csv")
        print(f"Cleaned players finished for season {season}")


add_position_to_clean()
add_costs_to_clean()
add_team_name_to_clean()
select_cols()

print("done")
