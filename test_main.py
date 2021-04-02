"""
The main testing file for BO and expressions
"""
import pandas as pd
import numpy as np
import time

from optimizer import Estimator
from expressions import Reactor, general_rate
from nextorch import plotting, bo, doe, utils, io

#%% Import and process data
# Set the reaction constants
stoichiometry = [-1, -3, 2]

data = pd.read_excel('ammonia_data.xlsx')
T = 623.0 # K

# Use the data at a single T only
data_single_T = data[np.array(data['Temperature (K)'], dtype = float) == T]
n_reactors = len(data_single_T)

# Select the pressure
pressures = np.array(data_single_T['Pressure (atm)'], dtype = float)

# Select the conversions
conversions = np.array(data_single_T['Conversion'], dtype = float)
conversions = np.expand_dims(conversions, axis = 1)
Y_experiments = conversions

# Selet the feed compositions
feed_ratios = np.array(data_single_T['Feed ratio (H2:N2)'], dtype = float)

# Select the residence time
times = np.array(data_single_T['Residence time (s)'], dtype = float)

# Select the weights
Y_weights = np.array(data_single_T['Weight'], dtype = float)

# Construct a list of dictionaries as Reactor inputs
reactor_data = []

for i in range(n_reactors):
    
    reactor_i = {}
    
    #reactor_i['temperature' ] = T
    reactor_i['P0'] = pressures[i]
    reactor_i['tf'] = times[i]
    
    feed_composition_i = np.zeros(3)
    feed_composition_i[0] = 1
    feed_composition_i[1] = feed_ratios[i]
    reactor_i['feed_composition'] = feed_composition_i
    
    reactor_data.append(reactor_i)


#%% Parameter estimation section
# Set the number of optimization loops
n_iter = 50

# Set the rate expression and parameter names 
para_names_1 = ['K', 'ksr', 'KA', 'KB']
rate_expression = general_rate

# Set the ranges for each parameter
para_ranges_1 = [[0.01, 0.5], 
                [0.01, 0.5],
                [0.01, 0.5],
                [0.01, 0.5]]


# start a timer
start_time = time.time()
estimator = Estimator(rate_expression, para_names_1, para_ranges_1, name = 'rate_1')
estimator.input_data(stoichiometry, reactor_data, Y_experiments, Y_weights)
X_opt, Y_opt, loss_opt, Exp = estimator.optimize(n_iter)
end_time= time.time()

# Print the results
file = open(estimator.name + ".txt","w")
file.write('Parameter estimation takes {:.2f} min \n'.format((end_time-start_time)/60))
file.write('Final loss {:.3f} \n'.format(loss_opt))
file.write('Parameters are {} \n'.format(X_opt))
file.close()

