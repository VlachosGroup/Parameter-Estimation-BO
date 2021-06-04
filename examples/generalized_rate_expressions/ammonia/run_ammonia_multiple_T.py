"""
Tests on temperature
"""
import os
import sys
import pandas as pd
import numpy as np
import time
from nextorch import plotting
from estimator.optimizer import BOOptimizer
from estimator.expressions import general_rate
from estimator.reactor import ModelBridge
import estimator.utils as ut


# %% Import and process data
# Set the reaction constants
stoichiometry = [-1, -3, 2]

data = pd.read_excel('ammonia_data.xlsx')
# Select only feed ratio = 3
data = data[data['Feed ratio (H2:N2)'] == 3]

n_reactors = len(data)

# Select the temperature
temperatures = np.array(data['Temperature (K)'], dtype=float)

# Select the pressure
pressures = np.array(data['Pressure (atm)'], dtype=float)

# Select the conversions
conversions = np.array(data['Conversion'], dtype=float)
conversions = np.expand_dims(conversions, axis=1)
Y_experiments = conversions

# Selet the feed compositions
feed_ratios = np.array(data['Feed ratio (H2:N2)'], dtype=float)

# Select the residence time
times = np.array(data['Residence time (s)'], dtype=float)

# Select the weights
Y_weights = np.array(data['Weight'], dtype=float)

# Construct a list of dictionaries as Reactor inputs
experimental_data = []

for i in range(n_reactors):
    experiment_i = {'temperature': temperatures[i], 'P0': pressures[i], 'tf': times[i]}
    feed_composition_i = np.zeros(3)
    feed_composition_i[0] = 1
    feed_composition_i[1] = feed_ratios[i]
    experiment_i['feed_composition'] = feed_composition_i
    experimental_data.append(experiment_i)

# %% Parameter estimation section
# estimator name 
estimator_name = 'ammonia_multiple_T_results'

# Set the number of optimization loops
n_iter = 50

# Set the rate expression and parameter names 
para_names_2 = ['K_prefactor', 'ksr_prefactor', \
                'KA_prefactor', 'KB_prefactor', \
                'K_Ea', 'ksr_Ea', 'KA_Ea', 'KB_Ea']

rate_expression = general_rate

# Set the ranges for each parameter
para_ranges_2 = [[0.1, 10],
                 [0.1, 10],
                 [0.1, 10],
                 [0.1, 10],
                 [-2, 0],
                 [-2, 0],
                 [-2, 0],
                 [-2, 0]]

# start a timer
start_time = time.time()

# Input experimental data and models (rate expressions) into a model bridge
bridge = ModelBridge(rate_expression, para_names_2, name=estimator_name)
bridge.input_data(stoichiometry, experimental_data, Y_experiments, Y_weights, qoi='conversion')

# set up an optimizer
optimizer = BOOptimizer(estimator_name)
X_opt, loss_opt, Exp = optimizer.optimize(bridge.loss_func, para_ranges_2, n_iter)
end_time = time.time()

# Predict the conversions given the optimal set of parameters
Y_opt = np.array(bridge.conversion(X_opt))
plotting.parity(Y_opt, Y_experiments)

# Print the results
ut.write_results(estimator_name, start_time, end_time, loss_opt, X_opt)
