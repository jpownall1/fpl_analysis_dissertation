import pickle
import matplotlib.pyplot as plt

# access results from pickle file, so I don't need to run this file over and over as it takes a very long time.
# rb means read byte for faster access
pickle_in = open("results_dict.pickle", "rb")
results_dict = pickle.load(pickle_in)


def convert_pos_to_word(position):
    position = position.upper()
    if position == "GK":
        return "Goalkeeper"
    elif position == "DEF":
        return "Defender"
    elif position == "MID":
        return "Midfielder"
    elif position == "FWD":
        return "Forward"
    else:
        raise ValueError("Invalid position")


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
    plt.title(f"Experimental Design results for position {convert_pos_to_word(position)} for season {season}")
    plt.legend()
    plt.show()


display_results(results_dict, "fwd_2020-21")


def get_ranked_params_position_as_latex_table(position, season):
    if season not in ["2016-17", "2017-18", "2018-19", "2019-20", "2020-21", "avg"]:
        raise ValueError("Not a valid season")
    print(r"""\begin{table}[ht]
\center
\begin{adjustbox}{width=1\textwidth}
\small
\begin{tabular}{ c c c }
Ranking & Variable & Average Accumulated Points\\
\hline""")
    for rp in results_dict[f"{position}_{season}_ranked_params"]:
        variable = rp[1].replace('_', r'\_')
        print(fr"{rp[0]} & {variable} & {int(rp[2])}\\")
    print(r"""\end{tabular}
\end{adjustbox}""")
    print(
        "\caption{Tabular representation of experimental design results for position " + position + " " + season + "}")
    print("\label{" + position + " " + season + " table}")
    print("\end{table}")


get_ranked_params_position_as_latex_table("gk", "avg")
