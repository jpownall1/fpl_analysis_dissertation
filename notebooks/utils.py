import pandas as pd


def switch_player_entry(entry, df_to_add, df_to_drop):
    """
    Method to switch a player from one dataframe to another with the same columns. Particularly useful when
    switching between starting 11 and subs

    params:
    entry - Pandas DF of one player entry i.e. the player to switch
    df_to_add - the dataframe to add the player to
    df_to_drop - the dataframe to drop the player from

    returns:
    df_to_add - the dataframe with the added player
    df_to_drop - the dataframe with the dropped player
    """
    # Ensure the entry has a unique index before adding it to df_to_add
    entry = entry.reset_index(drop=True)

    # Add the entry to df_to_add and reset the index
    df_to_add = pd.concat([df_to_add, entry]).reset_index(drop=True)

    # Find the index of the entry in df_to_drop
    index_to_drop = df_to_drop[df_to_drop.index.isin(entry.index)].index

    # Drop the entry from df_to_drop using the found index and reset the index
    df_to_drop = df_to_drop.drop(index_to_drop).reset_index(drop=True)

    return df_to_add, df_to_drop


def select_initial_starting_11(team, variable):
    team = team.sort_values(variable, ascending=False)
    starting_df = pd.DataFrame()
    sub_df = pd.DataFrame()

    # Select 1 goalkeeper
    gk = team[team.position == "GK"].head(1)
    starting_df, team = switch_player_entry(gk, starting_df, team)

    # Select at least 3 defenders
    defs = team[team.position == "DEF"].head(3)
    starting_df, team = switch_player_entry(defs, starting_df, team)

    # Select at least 1 forward
    fwd = team[team.position == "FWD"].head(1)
    starting_df, team = switch_player_entry(fwd, starting_df, team)

    # Select remaining positions
    remaining_positions = 7
    positions_selected = [p.position for p in starting_df.itertuples()]
    while remaining_positions > 0:
        if positions_selected.count("DEF") < 3:
            # Select defender if less than 3 defenders are already selected
            selected = team[team.position == "DEF"].head(1)
            starting_df, team = switch_player_entry(selected, starting_df, team)
            positions_selected.append("DEF")
            remaining_positions -= 1
        elif positions_selected.count("FWD") < 1:
            # Select forward if less than 1 forward is already selected
            selected = team[team.position == "FWD"].head(1)
            starting_df, team = switch_player_entry(selected, starting_df, team)
            positions_selected.append("FWD")
            remaining_positions -= 1
        else:
            # Select highest predicted points player from remaining players
            selected = team.head(1)
            starting_df, team = switch_player_entry(selected, starting_df, team)
            positions_selected.append(selected.iloc[0].position)
            remaining_positions -= 1

    sub_df = team

    # Print formation
    defenders_count = (starting_df.position == "DEF").sum()
    midfielders_count = (starting_df.position == "MID").sum()
    forwards_count = (starting_df.position == "FWD").sum()
    print(f"Formation is {defenders_count}-{midfielders_count}-{forwards_count}")

    return starting_df, sub_df


def select_captain(players_df):
    print("-----------------------CAPTAIN-----------------------")
    # Find the index of the player with the highest predicted_points
    highest_predicted_points_index = players_df['predicted_points'].idxmax()

    # Double the total_points value for that player
    players_df.loc[highest_predicted_points_index, 'total_points'] *= 2

    # Print the player with the highest predicted points
    captain_player = players_df.loc[highest_predicted_points_index]
    print(f"Selected captain: {captain_player['name']} with predicted points {captain_player['predicted_points'] }"
          f"and actual points {captain_player['total_points']/2} giving {captain_player['total_points']} points")

    # Return the modified DataFrame
    return players_df


def find_suitable_sub(earliest_kickoff_player, players_df, subs_df):
    gk_count = (players_df.position == "GK").sum()
    def_count = (players_df.position == "DEF").sum()
    mid_count = (players_df.position == "MID").sum()
    fwd_count = (players_df.position == "FWD").sum()

    suitable_subs = []

    for _, sub in subs_df.iterrows():
        if earliest_kickoff_player['position'] == 'GK' and gk_count > 1:
            if sub['position'] != 'GK':
                suitable_subs.append(sub)
        elif earliest_kickoff_player['position'] == 'DEF' and def_count > 3:
            suitable_subs.append(sub)
        elif earliest_kickoff_player['position'] == 'MID' and mid_count > 1:
            if sub['position'] != 'MID':
                suitable_subs.append(sub)
        elif earliest_kickoff_player['position'] == 'FWD' and fwd_count > 1:
            if sub['position'] != 'FWD':
                suitable_subs.append(sub)

    if suitable_subs:
        # Sort the list by predicted_points in descending order and return the first element
        suitable_subs.sort(key=lambda x: x['predicted_points'], reverse=True)
        return suitable_subs[0]
    else:
        return None


def sub_not_played_player(players_df, subs_df):
    print("-----------------------SUBSTITUTIONS-----------------------")
    zero_minutes_players = players_df[players_df['minutes'] == 0]

    # Error check: if there are no players with 0 minutes, return the original dataframes unmodified
    if len(zero_minutes_players) == 0:
        print("All players in the squad have played, no substitutions found.")
        return players_df, subs_df

    # Create a new DataFrame with updated 'kickoff_time' column to avoid SettingWithCopyWarning
    zero_minutes_players = zero_minutes_players.copy()
    zero_minutes_players['kickoff_time'] = pd.to_datetime(zero_minutes_players['kickoff_time'])

    earliest_kickoff_player = zero_minutes_players.loc[zero_minutes_players['kickoff_time'].idxmin()]

    # Find a player in the subs_df that can be switched with the earliest_kickoff_player while satisfying the formation constraints
    suitable_sub = find_suitable_sub(earliest_kickoff_player, players_df, subs_df)

    # Check if a switchable sub is found
    if suitable_sub is not None:
        print(f"Substitution: {earliest_kickoff_player['name']} -> {suitable_sub['name']}")

        # Convert earliest_kickoff_player and switchable_sub to DataFrames
        earliest_kickoff_player_df = earliest_kickoff_player.to_frame().T
        switchable_sub_df = suitable_sub.to_frame().T

        # Switch the earliest_kickoff_player with the switchable_sub
        players_df, subs_df = switch_player_entry(earliest_kickoff_player_df, subs_df, players_df)
        subs_df, players_df = switch_player_entry(switchable_sub_df, players_df, subs_df)
    else:
        print("No suitable substitution found.")

    return players_df, subs_df



def display_team(starting_df, subs_df):
    print("STARTING:")
    print(starting_df)
    print("SUBS:")
    print(subs_df)


def organise_team(players_df, variable):
    starting_df, subs_df = select_initial_starting_11(players_df, variable)
    starting_df, subs_df = sub_not_played_player(starting_df, subs_df)
    starting_df = select_captain(starting_df)
    display_team(starting_df, subs_df)

    return starting_df, subs_df
