"""
organise_team.py
----------------
This module provides functions to organise a football team using a pandas
DataFrame. It allows you to switch players between dataframes, select initial starting 11, substitutes, captain and
vice-captain, substitute players, validate squad sizes, and display team information.

Functions
---------
- switch_player_entry(entry: pd.DataFrame, df_to_add: pd.DataFrame, df_to_drop: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]
    Switches a player entry from one dataframe to another with the same columns, and returns the updated dataframes.

- select_initial_starting_11(team: pd.DataFrame, variable: str) -> Tuple[pd.DataFrame, pd.DataFrame]
    Selects the initial starting 11 and substitutes based on a given variable, and returns two dataframes: the starting
    11 and the substitutes.

- select_captain_and_vice_captain(players_df: pd.DataFrame, display: bool) -> Tuple[pd.DataFrame, str, str]
    Selects the captain and vice-captain based on the players_df, doubles their total_points if they have played, and
    returns the modified players_df and the names of the captain and vice-captain.

- get_available_positions_to_sub(earliest_kickoff_player: pd.Series, players_df: pd.DataFrame) -> List[str]
    Determines the available positions for substitution based on the earliest_kickoff_player and the current players_df,
    and returns a list of the available positions.

- find_suitable_sub(earliest_kickoff_player: pd.Series, players_df: pd.DataFrame, subs_df: pd.DataFrame) -> Union[pd.Series, None]
    Finds a suitable substitute for the earliest_kickoff_player from the subs_df based on available positions for
    substitution, and returns the selected substitute as a pandas Series, or None if no suitable substitute is found.

- sub_not_played_player(players_df: pd.DataFrame, subs_df: pd.DataFrame, display: bool) -> Tuple[pd.DataFrame, pd.DataFrame, str, str]
    Substitutes a player who has not played (0 minutes) from the players_df with a suitable substitute from the subs_df,
    considering formation constraints, and returns the updated dataframes and the names of the substituted player and
    substitute player.

- validate_squad_sizes(starting_df: pd.DataFrame, subs_df: pd.DataFrame, display: bool) -> None
    Validates the sizes of the starting and substitute squads and raises a ValueError if they are not the correct size.

- get_formation(starting_df: pd.DataFrame) -> str
    Calculates the formation of a football team based on the positions of players in the starting squad and returns a
    string representing the formation.

- display_team(starting_df: pd.DataFrame, subs_df: pd.DataFrame, display: bool) -> None
    Displays the team information, including formation and player details, if display is set to True.

- organise_team(players_df: pd.DataFrame, variable: str, display: bool=False) -> Tuple[pd.DataFrame, pd.DataFrame, str, str, str, str, str, str]
    Organises the team using the given players_df and variable, and returns the organized starting 11, substitutes,
    captain, vice-captain, substituted player, substitute player, and the total points of the team.
"""

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
    """
    Selects the initial starting 11 and substitutes from the given `team` dataframe, based on the given `variable`.
    Returns two dataframes: the starting 11 and the substitutes.

    Args:
        team (pd.DataFrame): The dataframe containing the players from which the initial starting 11 and substitutes
                             will be selected.
        variable (str): The variable based on which the initial starting 11 will be selected. This should be a column
                        name in the `team` dataframe.
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: A tuple containing two dataframes:
            starting_df (pd.DataFrame): The dataframe containing the starting 11 players.
            subs_df (pd.DataFrame): The dataframe containing the substitutes.
    """
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
    """
    Selects the captain and vice-captain from the given `players_df` dataframe, and doubles their total_points if the
    captain has played. Returns a tuple containing the modified `players_df` dataframe, and the names of the captain
    and vice-captain.

    Args:
        players_df (pd.DataFrame): The dataframe containing the players from which the captain and vice-captain will be selected.
        display (bool): If True, displays the console output. If False, the function does nothing.
    Returns:
        Tuple[pd.DataFrame, str, str]: A tuple containing the modified `players_df` dataframe, and the names of the
                                       captain and vice-captain:
            players_df (pd.DataFrame): The modified dataframe containing the updated total_points values.
            captain_name (str): The name of the captain.
            vice_captain_name (str): The name of the vice-captain.
    """
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
    """
    Determines the available positions for substitution based on the earliest_kickoff_player and the current players
    in the `players_df` dataframe. Returns a list of the available positions.

    Args:
        earliest_kickoff_player (pd.Series): A pandas Series containing the details of the earliest-kickoff player.
        players_df (pd.DataFrame): The dataframe containing the current players.

    Returns:
        List[str]: A list of available positions for substitution.
    """
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
    """
    Finds a suitable substitute from the `subs_df` dataframe for the `earliest_kickoff_player` based on available
    positions for substitution. Returns the selected substitute as a pandas Series, or None if no suitable substitute
    is found.

    Args:
        earliest_kickoff_player (pd.Series): A pandas Series containing the details of the earliest-kickoff player.
        players_df (pd.DataFrame): The dataframe containing the current players.
        subs_df (pd.DataFrame): The dataframe containing the substitute players.

    Returns:
        Union[pd.Series, None]: The selected substitute as a pandas Series, or None if no suitable substitute is found.
    """
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
    """
    Substitutes a player who has not played (0 minutes) from the players_df with a suitable substitute from the subs_df,
    considering formation constraints. If there is no suitable substitution or all players in the squad have played,
    the original dataframes are returned unmodified.
    Args:
    players_df (pd.DataFrame): A dataframe containing the players in the current squad.
    subs_df (pd.DataFrame): A dataframe containing the substitute players.
    display (bool): Whether to print out the substitution details.

    Returns:
        tuple: A tuple containing:
            - players_df (pd.DataFrame): The updated dataframe containing the players in the current squad after substitution.
            - subs_df (pd.DataFrame): The updated dataframe containing the substitute players after substitution.
            - earliest_kickoff_player_name (str): The name of the player with 0 minutes who has the earliest kickoff time.
            - suitable_sub_name (str): The name of the suitable substitute player, or None if no suitable substitution is found.
    """
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

    earliest_kickoff_player_name = earliest_kickoff_player['name']
    suitable_sub_name = suitable_sub['name']

    return players_df, subs_df, earliest_kickoff_player_name, suitable_sub_name


def validate_squad_sizes(starting_df, subs_df, display):
    """
        Validates the sizes of the starting and substitute squads and raises a ValueError if they are not the correct size.

        Args:
        - starting_df (pandas.DataFrame): A pandas dataframe containing the starting squad of players.
        - subs_df (pandas.DataFrame): A pandas dataframe containing the substitute squad of players.
        - display (bool): A boolean indicating whether to display a message if the validation passes.

        Raises:
        - ValueError: If the starting squad does not contain exactly 11 players or if the substitute squad does not contain
          exactly 4 players.

        Returns:
        - None: This function does not return anything. If the validation passes, a message is displayed if `display` is set
          to `True`.
        """
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
    """
    Calculates the formation of a football team based on the positions of players in the starting squad.

    Args:
    - starting_df (pandas.DataFrame): A pandas dataframe containing the starting squad of players.

    Returns:
    - str: A string representing the formation of the team in the format "DEF-MID-FWD", where DEF, MID and FWD are the
      number of defenders, midfielders and forwards respectively in the starting squad.
    """
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


def organise_team(players_df, variable, display=False):
    """
    Organizes the team by selecting the initial starting 11, choosing the captain and vice-captain, performing
    substitutions for players who did not play, validating squad sizes, and displaying the team.

    Args:
        players_df (pd.DataFrame): A dataframe containing the players in the current squad.
        variable (str): A string representing the variable on which the sorting will be based for selecting the starting 11.
        display (bool, optional): Whether or not to print out the team details. Defaults to False.

    Returns:
        tuple: A tuple containing:
            - starting_df (pd.DataFrame): The updated dataframe containing the players in the starting 11 after substitution.
            - subs_df (pd.DataFrame): The updated dataframe containing the substitute players after substitution.
    """
    starting_df, subs_df = select_initial_starting_11(players_df, variable)
    starting_df, captain, vice_captain = select_captain_and_vice_captain(starting_df, display)
    starting_df, subs_df, sub_off, sub_on = sub_not_played_player(starting_df, subs_df, display)
    validate_squad_sizes(starting_df, subs_df, display)
    display_team(starting_df, subs_df, display)

    return starting_df, subs_df
