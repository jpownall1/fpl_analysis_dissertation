from src.data.season_data import SeasonData
from src.data.player_data import PlayerData
from IPython.display import display


def calculate_players_total_points(players_df):
    total_points = players_df['total_points'].sum()
    return total_points


def calculate_teams_performance(season, position, subs, condition=""):
    if subs & (not condition): raise ValueError("If making subs, specify a condition")

    # define player data object to obtain player data
    player_data = PlayerData(season)
    players_df = player_data.select_random_players(3, position)

    # make sure position is upper case
    position = position.upper()

    points_track = [calculate_players_total_points(players_df)]

    gameweeks = sorted(player_data.get_all_players_curr_season_merged_gw_stats()['GW'].unique())
    for gameweek in gameweeks:
        # obtain a dataframe of all players for that gameweek
        all_players_df = player_data.get_all_players_curr_season_gw_stats(gameweek)

        # select only players of the position in question
        all_players_df = all_players_df[all_players_df.eval(f"position == '{position}'")]

        # get a list of the names already in the df
        players_names_list = players_df["name"].values

        # update current players with their new gameweek stats
        players_df = all_players_df[all_players_df['name'].isin(players_names_list)]

        # remove players already in random df from all players
        all_players_df = all_players_df[~all_players_df['name'].isin(players_names_list)]

        # find a player who does not meet condition, if there is one remove and add a player from all players who does
        if subs:
            players_not_meeting_condition = players_df.query("~(" + condition + ")")
            players_not_meeting_condition = players_not_meeting_condition[['name', 'total_points', 'was_home']]
            if not players_not_meeting_condition.empty:
                player_to_remove = players_not_meeting_condition.sample(1)
                players_df = players_df.drop(player_to_remove.index[0])
                players_meeting_condition = all_players_df.query(condition)
                player_to_add = players_meeting_condition.sample(1)
                players_df = players_df.append(player_to_add)

        display(players_df)
        points_track.append(calculate_players_total_points(players_df))

    # alter points track to show accumulation of points
    for i in range(1, len(points_track)):
        points_track[i] = points_track[i - 1] + points_track[i]

    print(points_track)


calculate_teams_performance("2019-20", "MID", True, "was_home == True")
