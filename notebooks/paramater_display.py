import pickle
import matplotlib.pyplot as plt

# access results from pickle file, so I don't need to run this file over and over as it takes a very long time.
# rb means read byte for faster access
pickle_in = open("results_dict.pickle", "rb")
results_dict = pickle.load(pickle_in)


def display_results(results, which_result):
    # plot results
    for key, value in results[which_result].items():
        if key == "no_subs":
            plt.plot(value, label=key, linewidth=3.0)
        else:
            plt.plot(value, label=key, linewidth=1.0)

    position = which_result.split("_")[0]
    season = which_result.split("_")[1]
    plt.xlabel("Gameweek")
    plt.ylabel("Average Points")
    plt.title(f"Results for season {season} with position {position}")
    plt.legend()
    plt.show()


print(results_dict[f"fwd_top_params"])
print(results_dict[f"mid_top_params"])
print(results_dict[f"def_top_params"])
print(results_dict[f"gk_top_params"])
display_results(results_dict, "fwd_avg")

