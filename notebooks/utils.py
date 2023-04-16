




def check_team_size(players_df, initial_players_df):
    if players_df.shape[0] != initial_players_df.shape[0]:
        raise ValueError(f"""Final team does not have correct amount of players. Something has gone wrong.
                             Number of players has been changed from {initial_players_df.shape[0]} to {players_df.shape[0]} 
                             {print(players_df)}""")