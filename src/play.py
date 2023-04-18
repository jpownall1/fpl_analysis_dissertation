"""
play.py: A script to simulate a fantasy football team's performance throughout a season.

The script uses linear programming to create an initial team and then simulates their performance
over the season, making transfers and captainsbased on the 'predicted_points' variable and simulating
the automatic changes an FPL team makes throughout the season.

Usage:
    Run the script using the command: python play.py

Dependencies:
    - notebooks.calculate_performance
    - notebooks.pick_team_lp
    - src.data.player_data
"""

from src.utils.calculate_performance import calculate_teams_performance
from src.analysis.pick_team_lp import make_initial_team_lp, get_selected_players_gw_one_data
from src.data.player_data import PlayerData

if __name__ == '__main__':
    # Get initial, unordered team from linear programming and left over budget
    season = "2021-22"
    selected_player_names, left_over_budget = make_initial_team_lp(season)

    # Add data from gameweek 1 for each player
    player_data = PlayerData(season)
    selected_players_df = get_selected_players_gw_one_data(player_data, selected_player_names)

    # Simulate season
    print(calculate_teams_performance(player_data, selected_players_df, "predicted_points", True, left_over_budget))
