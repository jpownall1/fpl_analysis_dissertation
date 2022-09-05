import pandas as pd

class DataLoader:
    def __init__(self):
        print("placeholder")
        self._data_location = '../data/historical_data/'

    def get_player_id_string(self, first_name, last_name, season):
        player_id_path = self._data_location + season + '/player_idlist.csv'
        df = pd.read_csv(player_id_path)
        df = df[(df['first_name'] == first_name) & (df['second_name'] == last_name)]
        player = df.head()
        player_id_string = (player['first_name'] + '_' + player['second_name'] + '_' +
                            player['id'])
        return player_id_string




    def get_player_historical_season_statistics(self, first_name, second_name, season: str, current_week: str, weeks: int):
        player_id = self.get_player_id_string(first_name, second_name)
        historical_player_data_path = self._data_location + season + '/players/' + player_id + '/history.csv'
        df = pd.read_csv(historical_player_data_path)

        return df