import pandas as pd
from sklearn.linear_model import LinearRegression

# for each position, find params from parameter analysis that yielded the highest accumulated points
pickle_in = open("results_dict.pickle", "rb")
results_dict = pickle.load(pickle_in)


gameweeks_dfs = []
for season in ["2016-17", "2017-18", "2018-19", "2019-20", "2020-21"]:
    gw_file = '../data/' + season + "/gws/merged_gw2.csv"
    gameweeks_dfs.append(pd.read_csv(gw_file, encoding="utf-8-sig"))

training_data = pd.concat(gameweeks_dfs)

models = {}
for pos in ["gk", "def", "mid", "fwd"]:
    # split the training data into two parts: the features, which are the independent variables, and the labels,
    # which are the dependent variables.
    features = training_data[results_dict[f"{pos}_top_params"]]
    labels = training_data["position"]

    # use the LinearRegression class from the scikit-learn library to train the linear regression model
    model = LinearRegression()
    model.fit(features, labels)

