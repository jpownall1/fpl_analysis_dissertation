import numpy as np

from player_data import PlayerData
from src.data.season_data import SeasonData
from team_data import TeamData
from IPython.display import display
import pandas as pd

player_data = PlayerData("Marcus", "Rashford", "2019-20")
df = player_data.get_player_historical_seasons_statistics()
display(df)

df = player_data.get_player_current_seasons_statistics(6)
display(df)

print("points_earned")
print(player_data.get_player_points_earned(11))

print("home_or_away")
print(player_data.is_player_home(11))

arsenal = TeamData(1,"2019-20")
display(arsenal.get_gameweek_fixture(1))

print(f"the team is {arsenal.get_team_name()}")
print(f"the opponent is {arsenal.get_opponent_name(1)}")
print("fav?")
print(arsenal.favourite_to_win(1))

season = SeasonData("2019-20")
#last_season_final_player_data
last_s_data = season.get_all_players_prev_season_stats()
last_s_data = last_s_data[['first_name', 'second_name', 'total_points']]
#display(last_s_data)

players_values = season.get_all_players_gw_stats(7)
#display(players_values)

def make_first_11(season):

    #get previous seasons player stats
    season = SeasonData(season)
    last_s_data = season.get_all_players_prev_season_stats()
    last_s_data = last_s_data[['first_name', 'second_name', 'total_points', 'minutes']]
    #remove players who have not played around 30 games
    last_s_data = last_s_data.drop(last_s_data[last_s_data.minutes < 90*30].index)

    #get current season player stats
    this_s_data = season.get_all_players_curr_season_stats()
    this_s_data = this_s_data[['first_name', 'second_name', 'initial_cost']]

    #merge together, this eliminates players who are newly promoted or relegated
    merged_df = pd.merge(last_s_data, this_s_data, on=["first_name", "second_name"])

    #find if players have changed teams?------------------------------------------------------------------------

    #derive points_per_mil, points_per_min and cpi
    merged_df['points_per_mil'] = np.where(merged_df['initial_cost'] != 0,
                                           merged_df['total_points']/merged_df['initial_cost'], 0)
    merged_df['points_per_min'] = np.where(merged_df['initial_cost'] != 0,
                                           merged_df['total_points']/merged_df['minutes'], 0)
    max_ppm = merged_df['points_per_mil'].max()
    max_ppmin = merged_df['points_per_min'].max()
    merged_df['cpi'] = merged_df.apply(lambda row: row['points_per_mil']/max_ppm + row['points_per_min']/max_ppmin,
                                       axis=1)

    return merged_df.sort_values(by=['cpi'], ascending=False)

display(make_first_11("2019-20"))