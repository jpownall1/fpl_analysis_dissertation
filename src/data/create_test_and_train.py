import pandas as pd
from pathlib import Path

path_to_data = str(Path(__file__).parent) + '/../../data/'

#get training data separated into positions for models

gameweeks_dfs = []
for season in ["2016-17", "2017-18", "2018-19", "2019-20", "2020-21"]:
    gw_file = path_to_data + season + "/gws/merged_gw2.csv"
    gameweeks_dfs.append(pd.read_csv(gw_file, encoding="utf-8-sig"))

training_data = pd.concat(gameweeks_dfs)
training_data_fwds = training_data[training_data['position'] == 'FWD']
training_data_mids = training_data[training_data['position'] == 'MID']
training_data_defs = training_data[training_data['position'] == 'DEF']
training_data_gks = training_data[training_data['position'] == 'GK']

training_data_fwds.to_csv(path_to_data + "test_and_train_data/fwds_train.csv", encoding="utf-8-sig", index=False)
training_data_mids.to_csv(path_to_data + "test_and_train_data/mids_train.csv", encoding="utf-8-sig", index=False)
training_data_defs.to_csv(path_to_data + "test_and_train_data/defs_train.csv", encoding="utf-8-sig", index=False)
training_data_gks.to_csv(path_to_data + "test_and_train_data/gks_train.csv", encoding="utf-8-sig", index=False)

#get test data separated into positions for models

test_data_file = path_to_data + "2021-22" + "/gws/merged_gw2.csv"
test_data = pd.read_csv(test_data_file, encoding="utf-8-sig")
test_data_fwds = test_data[test_data['position'] == 'FWD']
test_data_mids = test_data[test_data['position'] == 'MID']
test_data_defs = test_data[test_data['position'] == 'DEF']
test_data_gks = test_data[test_data['position'] == 'GK']

test_data_fwds.to_csv(path_to_data + "test_and_train_data/fwds_test.csv", encoding="utf-8-sig", index=False)
test_data_mids.to_csv(path_to_data + "test_and_train_data/mids_test.csv", encoding="utf-8-sig", index=False)
test_data_defs.to_csv(path_to_data + "test_and_train_data/defs_test.csv", encoding="utf-8-sig", index=False)
test_data_gks.to_csv(path_to_data + "test_and_train_data/gks_test.csv", encoding="utf-8-sig", index=False)


