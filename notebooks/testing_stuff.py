from src.data.season_data import SeasonData
from src.data.player_data import PlayerData
from IPython.display import display

player_data = PlayerData("2019-20")
mids = player_data.select_random_players(3, "position == 'MID'")
display(mids)