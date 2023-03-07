import pickle

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn import preprocessing

from pathlib import Path

data_location = str(Path(__file__).parent) + '/../data/test_and_train_data/'

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

for position in ["fwd", "mid", "def", "gk"]:

    # Split the data into training and testing sets
    train_data = pd.read_csv(data_location + position + "s_train.csv", encoding="utf-8", low_memory=False)
    train_data = train_data.dropna(subset=variables_dict[position])
    test_data = pd.read_csv(data_location + position + "s_test.csv", encoding="utf-8", low_memory=False)
    test_data = test_data.dropna(subset=variables_dict[position])

    # Define the input and output variables
    X_train = train_data[variables_dict[position]]
    # Fit scaler for standardisation and interpretability
    scaler = preprocessing.StandardScaler().fit(X_train)
    X_train_scaled = scaler.transform(X_train)
    Y_train = train_data['total_points']


    X_test = test_data[variables_dict[position]]
    X_test_scaled = scaler.transform(X_test)
    Y_test = test_data['total_points']

    # Create a linear regression model
    model = LinearRegression()

    # Train the model on the training data
    model.fit(X_train_scaled, Y_train)

    # Use the model to predict the number of points earned by the test samples
    Y_pred = model.predict(X_test_scaled)

    # Calculate the mean absolute error and root mean squared error
    mae = mean_absolute_error(Y_test, Y_pred)
    rmse = mean_squared_error(Y_test, Y_pred, squared=False)
    r2 = r2_score(Y_test, Y_pred)

    results_dict[position] = {
        "variables": variables_dict[position],
        "coefficients": model.coef_,
        "mean_absolute_error": mae,
        "root_mean_squared_error": rmse,
        "r_squared": r2,
        "model": model
    }

    # Print the results
    print(f"For {position}:")
    print(f"Mean absolute error: {mae}")
    print(f"Root mean squared error: {rmse}")
    print(f"R squared value: {r2}")

print("Saving to pickle file")
pickle_out = open("model_results_dict.pickle", "wb")
pickle.dump(results_dict, pickle_out)
pickle_out.close()
print("Pickle file saved as 'model_results_dict.pickle'")