automated_fantasy_football_player
==============================

This repository presents an approach to selecting players for an FPL team by using linear
regression to predict future player performance based on their recent performances, and
linear programming to optimise team selection given the previous season’s best group of
players within constraints.

It will analyse the usefulness of the points prediction in making informed decisions about
transfers and team organisation. It was found that this approach provided a significant
improvement in points accumulated by the end of the season compared to the average player.

Run python play.py for the outcome of the combination of techniques for season 2021-22.


Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    |
    ├── data              <- Directory for data.
    │   ├── 2016-17       <- Data from season 2016-17.
    │   ├── 2017-18       <- Data from season 2017-18.
    │   ├── 2018-19       <- Data from season 2018-19.
    │   ├── 2019-20       <- Data from season 2019-20.
    │   ├── 2020-21       <- Data from season 2020-21.
    │   ├── 2021-22       <- Data from season 2021-22.
    │   ├── test_and_train_data       <- Data used in training, testing and validating.
    │
    ├── reports            <- Generated analysis as LaTeX.
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── play.py    <- Simulation of season 2021-22 using linear programming and MLR to make decisions.
    │   │
    │   ├── data           <- Scripts to generate or manipulate data
    │   │   └── add_to_cleaned_players.py           <- Added team, position and initial cost to clean_players.
    │   │   └── add_to_merged_gameweeks.py           <- Added team, position and initial cost to clean_players.
    │   │   └── create_test_and_train.py           <- Creates test data from combining seasons 2016-17 to 2019-20,
    │   │   |                                         validation data from season 2020-21 and test from season
    │   │   |                                         2021-22.
    │   │   └── player_data.py           <- Used for extracting data for players.
    │   │   └── season_data.py           <- Used for extracting data for the season.
    │   │   └── team_data.py           <- Used for extracting data for teams.
    │   │
    │   ├── utils       <- Useful scripts used to carry out neccessary algorithms
    │   │   └── alter_results.py       <- To rename some dict keys and add data to individual variable analysis results.
    │   │   └── calculate_performance.py       <- Used to carry out algorithms measuring performances of teams.
    │   │   └── make_transfers.py       <- Used to simulate transfers.
    │   │   └── organise_team.py       <- Picks a team. Makes a sub if a player doesn't play, picks vice captain, organises
    |   |   |                             team formation.
    │   │   └── utils.py       <- Other useful functions.
    |   |
    │   ├── utils       <- Useful scripts used to carry out neccessary algorithms
    │   │   └── parameterised_model_analysis.py       <- Used to analyse values of parameters in linear regression model.
    │   │   └── variable_display.py       <- Used to analyse performance of individual variables on control teams.
    │   │
    │   ├── analysis         <- Scripts used to carry out experimental design, linear regression and linear programming.
    │   │   ├── indepemdent variable analysis.py         <- Experimental design file, randomly generates a small pool of
    |   |   |                                               players and bases transfers on them. Stores the accumulated
    |   |   |                                               points as a pickle file.
    │   │   └── parameterised_model.py         <- Creates a multiple linear regression model based on the training data
    |   |   |                                       file provided. Tests the model on validation and test data. Stores outcome
    |   |   |                                     of predicted points for the test data.
    |   │   └── pick_team_lp.py         <- Creates a team of players by maximising the possible total points earnt from
    |   |                                  all team players in the previous season, extracting the names of those players
    |   |                                  and uses that team as a starting squad for the next season.


--------
