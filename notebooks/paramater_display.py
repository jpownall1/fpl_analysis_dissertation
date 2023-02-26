import pickle
import matplotlib.pyplot as plt
import parameter_analysis

# access results from pickle file, so I don't need to run this file over and over as it takes a very long time.
# rb means read byte for faster access
pickle_in = open("results_dict.pickle", "rb")
results_dict = pickle.load(pickle_in)

print(results_dict)
def display_results(results, which_result):
    ordered_params = [t[1] for t in results_dict[f"{which_result}_ranked_params"]]
    # plot results
    for key in ordered_params:
        if key == "no_transfers":
            plt.plot(results[which_result][key], label=key, linewidth=3.0)
        else:
            plt.plot(results[which_result][key], label=key, linewidth=1.0)

    position = which_result.split("_")[0]
    season = which_result.split("_")[1]
    plt.xlabel("Gameweek")
    plt.ylabel("Average Points")
    plt.title(f"{position} {season} results")
    plt.legend()
    plt.show()


display_results(results_dict, "fwd_avg")


def print_ranked_params_position(position):
    print(f"For position {position}:")
    for season in ["2016-17", "2017-18", "2018-19", "2019-20", "2020-21", "avg"]:
        print(f"Season {season}:")
        print(results_dict[f"{position}_{season}_ranked_params"])


for position in ["gk", "def", "mid", "fwd"]:
    print_ranked_params_position(position)
