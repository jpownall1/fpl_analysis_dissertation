"""
This module, season_data.py, defines a class SeasonData to interact with and
retrieve various types of season data for Fantasy Premier League (FPL) analysis.

The SeasonData class includes methods to:

Retrieve data for a specific season.
Get team information for a specific season.
Get fixture information for a specific season.
Get fixture information for a specific gameweek within a season.
"""


import pandas as pd
from pathlib import Path


class SeasonData:
    def __init__(self, season):
        print("placeholder")
        self._data_location = str(Path(__file__).parent) + '/../../data/' + season + "/"
        self._season = season

    def get_teams(self):
        path = self._data_location + 'teams.csv'
        df = pd.read_csv(path)
        return df

    def get_fixtures(self):
        path = self._data_location + 'fixtures.csv'
        df = pd.read_csv(path)
        return df

    def get_gameweek_fixtures(self, gameweek):
        df = self.get_fixtures()
        df = df[df["event"] == gameweek]
        return df





