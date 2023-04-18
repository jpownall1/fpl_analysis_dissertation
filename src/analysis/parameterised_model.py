"""
paramaterised_model.py
This module trains different types of linear regression models (Standard, Lasso, and Ridge) on
historical football player performance data for each position (Forward, Midfielder, Defender,
and Goalkeeper) and predicts the total points scored for given test and validation datasets.

Functions
get_linear_regression_results(type, add_predicted_points_to_file=False):
Trains a specified type of linear regression model on the training data and predicts total
points for test and validation datasets, printing the results to the console. Optionally,
the predicted points can be added to a file.

Notes
This module assumes that the data files are located in a folder relative to the script.
The data_location variable should be set accordingly.
Requires the following libraries: numpy, pandas, scikit-learn, pathlib
The results_dict will store model results, including Mean Absolute Error (MAE),
Root Mean Squared Error (RMSE), R-squared, and model coefficients.
"""

import pickle
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Lasso, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn import preprocessing
from pathlib import Path

from sklearn.model_selection import GridSearchCV

data_location = str(Path(__file__).parent) + '/../../data/test_and_train_data/'

variables_dict = {
    "fwd": ["recent_goals_scored", "recent_clean_sheets", "recent_assists", "recent_yellow_cards",
            "recent_goals_conceded", "was_home"],
    "mid": ["recent_goals_scored", "recent_assists", "recent_clean_sheets", "recent_goals_conceded",
            "recent_creativity", "was_home"],
    "def": ["recent_assists", "recent_clean_sheets", "recent_goals_scored", "recent_creativity",
            "recent_yellow_cards", "was_home"],
    "gk": ["recent_clean_sheets", "recent_assists", "recent_saves", "recent_total_points",
           "recent_minutes", "was_home"]
}

results_dict = {}


def get_linear_regression_results(type, add_predicted_points_to_file=False):
    """
    Trains a linear regression model on the train_data for each position and then predicts
    total_points for the test_data and validation_data. The results of the predictions are
    stored in a dictionary and printed to the console. Optionally, the predicted points can
    be added to a file.

    Parameters
    ----------
    type : str
        Type of linear regression model to be used. Can be "standard", "lasso", or "ridge".
    add_predicted_points_to_file : bool, optional
        If True, the predicted points for each player will be added to a new file.
        Default is False.

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If the type is not one of the following: "standard", "lasso", or "ridge".

    Notes
    -----
    This function assumes the data files are located in a folder relative to the script.
    The data_location variable should be set accordingly.
    """
    list_of_positions_with_pp = []

    for position in ["fwd", "mid", "def", "gk"]:

        # Split the data into train, test and validation sets
        train_data = pd.read_csv(data_location + position + "s_train.csv", encoding="utf-8", low_memory=False)
        train_data = train_data.dropna(subset=variables_dict[position])
        test_data = pd.read_csv(data_location + position + "s_test.csv", encoding="utf-8", low_memory=False)
        test_data = test_data.dropna(subset=variables_dict[position])
        validation_data = pd.read_csv(data_location + position + "s_validation.csv", encoding="utf-8", low_memory=False)
        validation_data = validation_data.dropna(subset=variables_dict[position])

        # Get training data separated into objective value and variables, also fit scalar and scale variables
        X_train = train_data[variables_dict[position]]
        # Fit scaler for standardisation and interpretability
        scaler = preprocessing.StandardScaler().fit(X_train)
        X_train_scaled = scaler.transform(X_train)
        Y_train = train_data['total_points']

        # Get test data separated into objective value and variables, also scale variables
        X_test = test_data[variables_dict[position]]
        X_test_scaled = scaler.transform(X_test)
        Y_test = test_data['total_points']

        # Get test data separated into objective value and variables, also scale variables
        X_validation = validation_data[variables_dict[position]]
        X_validation_scaled = scaler.transform(X_validation)
        Y_validation = validation_data['total_points']

        # Create a linear regression model
        if type == "standard":
            model = LinearRegression()
        elif type == "lasso":
            # Use GridSearchCV to find the best alpha
            alphas = np.arange(0.00001, 0.002, 0.00001)
            model = GridSearchCV(Lasso(), {'alpha': alphas})
        elif type == "ridge":
            # Use GridSearchCV to find the best alpha
            alphas = np.arange(1, 320, 1)
            model = GridSearchCV(Ridge(), {'alpha': alphas})

        # Train the model on the training data
        model.fit(X_train_scaled, Y_train)

        if type != "standard":
            # print(model.cv_results_)
            model = model.best_estimator_

        # Use the model to predict the number of points earned by the test samples
        Y_pred = model.predict(X_test_scaled)

        if add_predicted_points_to_file:
            test_data["predicted_points"] = Y_pred
            list_of_positions_with_pp.append(test_data)

        # Calculate the mean absolute error and root mean squared error
        mae = mean_absolute_error(Y_test, Y_pred)
        rmse = mean_squared_error(Y_test, Y_pred, squared=False)
        r2 = r2_score(Y_test, Y_pred)

        # Initialise results key for position
        results_dict[position] = {}

        results_dict[position]["test"] = {
            "variables": variables_dict[position],
            "coefficients": model.coef_,
            "mean_absolute_error": mae,
            "root_mean_squared_error": rmse,
            "r_squared": r2,
            "model": model
        }

        # Print the results for test
        print(f"----------------------------------------For {position}, the test set:")
        print(f"Mean absolute error: {mae}")
        print(f"Root mean squared error: {rmse}")
        print(f"R squared value: {r2}")

        if type == "lasso" or type == "ridge":
            results_dict[position]["optimal_alpha"] = model.alpha
            print(f"Alpha value for {type} model: {model.alpha}")

        # Use the model to predict the number of points earned by the validation samples
        Y_pred_valid = model.predict(X_validation_scaled)

        # Calculate the mean absolute error and root mean squared error
        mae_valid = mean_absolute_error(Y_validation, Y_pred_valid)
        rmse_valid = mean_squared_error(Y_validation, Y_pred_valid, squared=False)
        r2_valid = r2_score(Y_validation, Y_pred_valid)

        results_dict[position]["validation"] = {
            "variables": variables_dict[position],
            "coefficients": model.coef_,
            "mean_absolute_error": mae_valid,
            "root_mean_squared_error": rmse_valid,
            "r_squared": r2_valid,
            "model": model
        }

        # Print the results for validation
        print(f"------------------------------------------------For {position}, the validation set:")
        print(f"Mean absolute error: {mae_valid}")
        print(f"Root mean squared error: {rmse_valid}")
        print(f"R squared value: {r2_valid}")
        print(f"Coefficients: {model.coef_}")

        if type == "lasso" or type == "ridge":
            results_dict[position]["optimal_alpha"] = model.alpha
            print(f"Alpha value for {type} model: {model.alpha}")

    list_of_mae_test = []
    list_of_mae_valid = []
    for position in ["fwd", "mid", "def", "gk"]:
        list_of_mae_test.append(results_dict[position]["test"]["mean_absolute_error"])
        list_of_mae_valid.append(results_dict[position]["validation"]["mean_absolute_error"])

    print("------------------------------------------------------------------------------------------")
    print(f"The average mae on the test for {type} is {sum(list_of_mae_test) / len(list_of_mae_test)}")
    print(f"The average mae on the validation for {type} is {sum(list_of_mae_valid) / len(list_of_mae_valid)}")

    if add_predicted_points_to_file:
        merged_gw_df = pd.concat(list_of_positions_with_pp, axis=0)
        merged_gw_df.to_csv(data_location + "2021-22_merged_gws_alpha.csv", encoding="utf-8-sig", index=False)
        print(f"File 2021-22_merged_gws_alpha.csv made at {data_location}")


if __name__ == "__main__":
    get_linear_regression_results("standard", True)
    print()
    print("Saving to pickle file")
    pickle_out = open("../visualisation/model_results_dict.pickle", "wb")
    pickle.dump(results_dict, pickle_out)
    pickle_out.close()
    print("Pickle file saved as 'model_results_dict.pickle'")
