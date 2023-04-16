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
    # Store the original index of the entry before resetting it
    original_index = entry.index

    # Ensure the entry has a unique index before adding it to df_to_add
    entry = entry.reset_index(drop=True)

    # Add the entry to df_to_add and reset the index
    df_to_add = pd.concat([df_to_add, entry]).reset_index(drop=True)

    # Drop the entry from df_to_drop using the original index and reset the index
    df_to_drop = df_to_drop.drop(original_index).reset_index(drop=True)

    return df_to_add, df_to_drop


def select_initial_starting_11(team, variable):
    team = team.sort_values(variable, ascending=False)
    starting_df = pd.DataFrame()
    subs_df = pd.DataFrame()

    # Select 1 goalkeeper
    gk = team[team.position == "GK"].head(1)
    starting_df, team = switch_player_entry(gk, starting_df, team)

    # Select at least 3 defenders
    defs = team[team.position == "DEF"].head(3)
    starting_df, team = switch_player_entry(defs, starting_df, team)

    # Select at least 3 midfielders
    mids = team[team.position == "MID"].head(3)
    starting_df, team = switch_player_entry(mids, starting_df, team)

    # Select at least 1 forward
    fwd = team[team.position == "FWD"].head(1)
    starting_df, team = switch_player_entry(fwd, starting_df, team)

    # Fill the remaining positions with the highest predicted points players, excluding goalkeepers
    remaining_positions = 3
    top_players = team[team.position != "GK"].head(remaining_positions)
    starting_df, team = switch_player_entry(top_players, starting_df, team)

    subs_df = team

    return starting_df, subs_df


def select_captain_and_vice_captain(players_df, display):
    if display:
        print("-----------------------CAPTAIN & VICE-CAPTAIN-----------------------")
    # Find the index of the player with the highest predicted_points
    highest_predicted_points_index = players_df['predicted_points'].idxmax()

    # Find the index of the player with the second highest predicted_points
    players_no_captain = players_df.drop(highest_predicted_points_index)
    second_highest_predicted_points_index = players_no_captain['predicted_points'].idxmax()

    captain_player = players_df.loc[highest_predicted_points_index]
    vice_captain_player = players_df.loc[second_highest_predicted_points_index]

    # Check if the captain has played that week
    if captain_player['minutes'] == 0:
        # Double the total_points value for the vice-captain
        players_df.loc[second_highest_predicted_points_index, 'total_points'] *= 2
        if display:
            print(f"Captain {captain_player['name']} has not played this week.")
            print(
                f"Selected vice-captain: {vice_captain_player['name']} with predicted points {vice_captain_player['predicted_points']}"
                f" and actual points {vice_captain_player['total_points']} giving {vice_captain_player['total_points'] * 2} points")
    else:
        # Double the total_points value for the captain
        players_df.loc[highest_predicted_points_index, 'total_points'] *= 2
        if display:
            print(f"Selected captain: {captain_player['name']} with predicted points {captain_player['predicted_points']}"
                  f" and actual points {captain_player['total_points']} giving {captain_player['total_points'] * 2} points")
            print(
                f"Selected vice-captain: {vice_captain_player['name']} with predicted points {vice_captain_player['predicted_points']}")

    # Return the modified DataFrame
    return players_df, captain_player['name'], vice_captain_player['name']


def get_available_positions_to_sub(earliest_kickoff_player, players_df):
    def_count = (players_df.position == "DEF").sum()
    mid_count = (players_df.position == "MID").sum()
    fwd_count = (players_df.position == "FWD").sum()

    available_positions = []

    if earliest_kickoff_player['position'] == 'GK':
        available_positions.append('GK')
    else:
        if earliest_kickoff_player['position'] == 'DEF':
            def_count -= 1
        elif earliest_kickoff_player['position'] == 'MID':
            mid_count -= 1
        elif earliest_kickoff_player['position'] == 'FWD':
            fwd_count -= 1

        if def_count + 1 == 3:
            return ["DEF"]
        if mid_count + 1 == 3:
            return ["MID"]
        if fwd_count + 1 == 1:
            return ["FWD"]

        if def_count + 1 > 3:
            available_positions.append('DEF')
        if mid_count + 1 > 3:
            available_positions.append('MID')
        if fwd_count + 1 > 1:
            available_positions.append('FWD')

    return available_positions


def find_suitable_sub(earliest_kickoff_player, players_df, subs_df):
    available_positions = get_available_positions_to_sub(earliest_kickoff_player, players_df)
    suitable_subs = []

    for _, sub in subs_df.iterrows():
        if sub['position'] in available_positions:
            suitable_subs.append(sub)

    if suitable_subs:
        # Sort the list by predicted_points in descending order and return the first element
        suitable_subs.sort(key=lambda x: x['predicted_points'], reverse=True)
        return suitable_subs[0]
    else:
        return None


def sub_not_played_player(players_df, subs_df, display):
    if display:
        print("-----------------------SUBSTITUTIONS-----------------------")
    zero_minutes_players = players_df[players_df['minutes'] == 0]

    # Error check: if there are no players with 0 minutes, return the original dataframes unmodified
    if len(zero_minutes_players) == 0:
        if display:
            print("All players in the squad have played, no substitutions found.")
        return players_df, subs_df, None, None

    # Create a new DataFrame with updated 'kickoff_time' column to avoid SettingWithCopyWarning
    zero_minutes_players = zero_minutes_players.copy()
    zero_minutes_players['kickoff_time'] = pd.to_datetime(zero_minutes_players['kickoff_time'])

    earliest_kickoff_player = zero_minutes_players.loc[zero_minutes_players['kickoff_time'].idxmin()]

    # Find a player in the subs_df that can be switched with the earliest_kickoff_player while satisfying the
    # formation constraints
    suitable_sub = find_suitable_sub(earliest_kickoff_player, players_df, subs_df)

    # Check if a switchable sub is found
    if suitable_sub is not None:
        if display:
            print(f"Substitution: {earliest_kickoff_player['name']} -> {suitable_sub['name']}")

        # Convert earliest_kickoff_player and switchable_sub to DataFrames
        earliest_kickoff_player_df = earliest_kickoff_player.to_frame().T
        suitable_sub_df = suitable_sub.to_frame().T

        # Switch the earliest_kickoff_player with the switchable_sub
        subs_df, players_df = switch_player_entry(earliest_kickoff_player_df, subs_df, players_df)
        players_df, subs_df = switch_player_entry(suitable_sub_df, players_df, subs_df)
    else:
        if display:
            print("No suitable substitution found.")

    return players_df, subs_df, earliest_kickoff_player['name'], suitable_sub['name']


def validate_squad_sizes(starting_df, subs_df, display):
    starting_count = starting_df.shape[0]
    subs_count = subs_df.shape[0]

    if starting_count != 11 and subs_count != 4:
        raise ValueError(f"The starting_df should have 11 players, but it has {starting_count} players. Also,"
                         f"The subs_df should have 4 players, but it has {subs_count} players.\n"
                         f"{display_team(starting_df, subs_df)}")

    if starting_count != 11:
        raise ValueError(f"The starting_df should have 11 players, but it has {starting_count} players.")

    if subs_count != 4:
        raise ValueError(f"The subs_df should have 4 players, but it has {subs_count} players.")

    if display:
        print("Squad size validation passed. Starting 11 and subs have correct number of players.")


def get_formation(starting_df):
    # Count the number of DEFs, MIDs, and FWDs in the starting_df
    def_count = (starting_df.position == "DEF").sum()
    mid_count = (starting_df.position == "MID").sum()
    fwd_count = (starting_df.position == "FWD").sum()

    return f"{def_count}-{mid_count}-{fwd_count}"


def display_team(starting_df, subs_df, display):
    if display:
        # Print the formation
        print(f"Formation: {get_formation(starting_df)}")

        print("STARTING:")
        print(starting_df)
        print("SUBS:")
        print(subs_df)


def organise_team(players_df, variable, player_transferred_out, player_transferred_in, delta_value, budget, display=False):
    starting_df, subs_df = select_initial_starting_11(players_df, variable)
    starting_df, captain, vice_captain = select_captain_and_vice_captain(starting_df, display)
    starting_df, subs_df, sub_off, sub_on = sub_not_played_player(starting_df, subs_df, display)
    validate_squad_sizes(starting_df, subs_df, display)
    display_team(starting_df, subs_df, display)
    gameweek = players_df.iloc[0]['GW']
    string = fr"{int(gameweek)} & {int(budget)} & {player_transferred_out} & {player_transferred_in} & {round(delta_value, 4)} & {sub_off} & {sub_on} & {get_formation(starting_df)} \\"
    string = string.replace('_', ' ')
    print(string)

    return starting_df, subs_df
