from notebooks.calculate_performance import calculate_teams_performance
from notebooks.pick_team_lp import make_initial_team_lp, get_selected_players_gw_data
from src.data.player_data import PlayerData

# get initial, unordered team and left over budget
season = "2021-22"
both = make_initial_team_lp(season)
selected_player_names = both[0]
left_over_budget = both[1]
player_data = PlayerData(season)
selected_players_df = get_selected_players_gw_data(player_data, selected_player_names)


# put team into calculate teams performance
print(calculate_teams_performance(player_data, selected_players_df, "predicted_points", True, left_over_budget))
