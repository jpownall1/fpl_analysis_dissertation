from src.data.season_data import SeasonData
from IPython.display import display

def make_first_11(season):
    season = SeasonData(season)
    #last_season_final_player_data
    last_s_data = season.get_teams()
    #last_s_data = last_s_data[['name', 'total_points']]
    #remove teams that are no longer in the pl
    return last_s_data

display(make_first_11("2019-20"))