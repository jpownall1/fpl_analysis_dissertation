import pickle
import matplotlib.pyplot as plt
import numpy as np


# access results from pickle file, so I don't need to run this file over and over as it takes a very long time.
# rb means read byte for faster access
pickle_in = open("model_results_dict.pickle", "rb")
results_dict = pickle.load(pickle_in)

print(results_dict)

def make_parameter_bar_chart(position):
    x = results_dict[position]["variables"]
    y = results_dict[position]["coefficients"]

    fig, ax = plt.subplots()
    ax.bar(x, y)

    ax.set_xlabel('Variables')
    ax.set_ylabel('Coefficients')
    ax.set_title(f'Relation of parameterised model coefficients for position {position}')
    ax.set_facecolor('whitesmoke')

    plt.show()

make_parameter_bar_chart("fwd")