import pandas as pd
from IPython.core.display import display

from src.data.player_data import PlayerData

seasons = ["2016-17"]  # , "2017-18", "2018-19", "2019-20", "2020-21", "2021-22"]


def add_team_to_gameweeks():
    for season in seasons:
        gw_file = '../../data/' + season + "/gws/merged_gw.csv"
        gameweeks_df = pd.read_csv(gw_file, encoding="ISO-8859-1")

        if 'team' not in gameweeks_df.columns:
            file = '../../data/' + season + "/cleaned_players.csv"
            clean_df = pd.read_csv(file, encoding="ISO-8859-1")
            # this is due to name column changing from name to name with player id
            if season in ["2016-17", "2017-18"]:
                clean_df['name'] = clean_df.apply(lambda row: row["first_name"] + "_" + row["second_name"], axis=1)
            else:
                idlist_file = '../../data/' + season + '/player_idlist.csv'
                id_df = pd.read_csv(idlist_file, encoding="ISO-8859-1")
                clean_df = pd.merge(clean_df, id_df, on=["first_name", "second_name"])
                clean_df['name'] = clean_df.apply(lambda row: row['first_name'] + '_' + row['second_name'] +
                                                              '_' + str(row['id']), axis=1)
            clean_df.rename(columns={'team_name': 'team'}, inplace=True)
            # clean_df = clean_df.rename({'team_name': 'team'})
            clean_df = clean_df[['name', 'team']]
            clean_df = pd.merge(gameweeks_df, clean_df, on=["name"])
            clean_df.to_csv(gw_file)
            print(f"Team added for season {season}")
        else:
            print(f"Team already in data for season {season}")


def add_position_to_gameweeks():
    for season in seasons:
        gw_file = '../../data/' + season + "/gws/merged_gw.csv"
        gameweeks_df = pd.read_csv(gw_file, encoding="ISO-8859-1")

        file = '../../data/' + season + "/cleaned_players.csv"
        clean_df = pd.read_csv(file, encoding="ISO-8859-1")

        if 'position' not in gameweeks_df.columns:

            # this is due to name column changing from name to name with player id
            if season in ["2016-17", "2017-18"]:
                clean_df['name'] = clean_df.apply(lambda row: row["first_name"] + "_" + row["second_name"], axis=1)
            else:
                idlist_file = '../../data/' + season + '/player_idlist.csv'
                id_df = pd.read_csv(idlist_file, encoding="ISO-8859-1")
                clean_df = pd.merge(clean_df, id_df, on=["first_name", "second_name"])
                clean_df['name'] = clean_df.apply(lambda row: row['first_name'] + '_' + row['second_name'] +
                                                              '_' + str(row['id']), axis=1)

            clean_df = clean_df[['name', 'position', 'team_name']]
            clean_df.rename(columns={'team_name': 'team'}, inplace=True)
            clean_df = pd.merge(gameweeks_df, clean_df, on=["name", "team"])
            clean_df.to_csv(gw_file)
            print(f"Position added for season {season}")
        else:
            print(f"Position already in data for season {season}")


def add_recent_stats(column_name):
    for season in seasons:
        gw_file = '../../data/' + season + "/gws/merged_gw.csv"
        gameweeks_df = pd.read_csv(gw_file, encoding="ISO-8859-1")

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
            print(gameweek_subsets)
            for subset in gameweek_subsets:
                subset_df = gameweeks_df[gameweeks_df['GW'].isin(subset)]
                df_totals = subset_df.groupby('name')[column_name].sum().to_frame(name='recent_' + column_name)
                df_totals = df_totals.reset_index()
                # have to do it this way for the gameweek value inconsistency, to put it onto the next gw
                df_totals["GW"] = gameweeks[gameweeks.index(subset[len(subset) - 1]) + 1]
                # df_totals["GW"] = subset[len(subset)-1]

                to_merge_df_list.append(df_totals)

            to_merge_df = pd.concat(to_merge_df_list)
            gameweeks_df = pd.merge(gameweeks_df, to_merge_df, on=["name", "GW"])
            print(gameweeks_df[['name', 'GW', column_name, 'recent_' + column_name]])

            # save new merged_gw dataframe
            # gameweeks_df.to_csv(gw_file)
            gameweeks_df.to_csv('../../data/' + season + "/gws/merged_gw2.csv")

            print(f"Recent goals added for season {season}")
        else:
            print(f"Recent goals already in data for season {season}")


def select_cols():
    cols = ['opponent_team', 'assists', 'threat', 'selected', 'bonus', 'ict_index', 'fixture', 'red_cards', 'was_home',
            'bps', 'round', 'penalties_missed', 'minutes', 'team', 'name', 'transfers_balance', 'value', 'team_a_score',
            'clean_sheets', 'GW', 'transfers_in', 'transfers_out', 'element', 'penalties_saved', 'goals_scored',
            'yellow_cards', 'influence', 'total_points', 'creativity', 'position', 'goals_conceded', 'saves',
            'own_goals', 'kickoff_time', 'team_h_score']


# add_team_to_gameweeks()
# add_position_to_gameweeks()
add_recent_stats("goals_scored")

print("done")
