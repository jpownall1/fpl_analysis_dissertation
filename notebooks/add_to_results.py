import pickle
import parameter_analysis

# access results from pickle file, so I don't need to run this file over and over as it takes a very long time.
# rb means read byte for faster access
pickle_in = open("results_dict.pickle", "rb")
results_dict = pickle.load(pickle_in)

# get average points across all seasons for each param
results_dict["gk_avg"] = parameter_analysis.get_average_dict(results_dict, "gk")
results_dict["def_avg"] = parameter_analysis.get_average_dict(results_dict, "def")
results_dict["mid_avg"] = parameter_analysis.get_average_dict(results_dict, "mid")
results_dict["fwd_avg"] = parameter_analysis.get_average_dict(results_dict, "fwd")

# get top params for each position
for pos in ["gk", "def", "mid", "fwd"]:
    for season in ["2016-17", "2017-18", "2018-19", "2019-20", "2020-21", "avg"]:
        results_dict[f"{pos}_{season}_ranked_params"] = parameter_analysis.get_ordered_top_params_tuples(results_dict, pos, season)

del results_dict["fwd_top_params"]
del results_dict["mid_top_params"]
del results_dict["def_top_params"]
del results_dict["gk_top_params"]




# save results as pickle file, so I don't need to run this file over and over as it takes a very long time.
# wb means with byte for faster access
print("Saving to pickle file")
pickle_out = open("results_dict.pickle", "wb")
pickle.dump(results_dict, pickle_out)
pickle_out.close()
print("Pickle file saved as 'results_dict.pickle'")
