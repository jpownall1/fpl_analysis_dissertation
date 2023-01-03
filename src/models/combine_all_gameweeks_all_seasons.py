import pandas as pd
from IPython.core.display import display

seasons = ["2016-17", "2017-18", "2018-19", "2019-20", "2020-21", "2021-22"]
def combine_all_gameweeks_all_seasons():
    all_gameweek_dfs = []
    for season in seasons:
        file = '../../data/historical_data/' + season + "/gws/merged_gw.csv"
        gw_df = pd.read_csv(file, encoding="ISO-8859-1")
        all_gameweek_dfs.append(gw_df)
    all_seasons_gameweeks_data = pd.concat(all_gameweek_dfs)

    return all_seasons_gameweeks_data

#display(combine_all_gameweeks_all_seasons())

file = '../../data/historical_data/' + "2016-17" + "/gws/merged_gw.csv"
s1_df = pd.read_csv(file, encoding="ISO-8859-1")

file = '../../data/historical_data/' + "2021-22" + "/gws/merged_gw.csv"
s2_df = pd.read_csv(file, encoding="ISO-8859-1")

print(set(s1_df.columns) - set(s2_df.columns))
print(set(s2_df.columns) - set(s1_df.columns))
print(set(s2_df.columns) & set(s1_df.columns))