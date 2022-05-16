#!/usr/bin/env python

import os
import shutil
import subprocess

import numpy as np
from smt.sampling_methods import LHS

xlimits = np.array([[1.0, 10.0], [800.0, 1000.0], [1.0, 5.00]])
sampling = LHS(xlimits=xlimits)
num = 30
x = sampling(num)
basedir = os.getcwd()
list_of_dirs = [("P_" + str(round(p, 2)) + "_T_" + str(round(T)) + "_volflow_" + str(round(Q, 2)), round(p, 2),
                 round(T, 2), round(Q, 2))
                for p, T, Q in x]
print(list_of_dirs)
print(len(list_of_dirs))
for (name, pval, Tval, Qval) in list_of_dirs:
    if not os.path.isdir(name): os.mkdir(name)
    os.chdir(name)
    shutil.copy2(basedir + "/thermo.xml", "thermo.xml")
    file = open(name + '.sq', 'w')
    file.write("""#!/bin/bash -l
# SLURM or other job manager settings to be added here 
# ...
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --job-name='""" + name + """'
# ... 

# setup the environment to run OpenMKM 
# . /opt/shared/slurm/templates/libexec/openmp.sh
# vpkg_require openmkm/20210831:gcc9

# run OpenMKM like so
omkm reactor.yaml thermo.xml
""")
    file.close()
    file = open('reactor.yaml', 'w')
    file.write("""# File generated by pMuTT (v 1.2.21) on 2020-07-09 16:03:04.988190
# See documentation for OpenMKM YAML file here:
# https://vlachosgroup.github.io/openmkm/input
inlet_gas:
    flow_rate: \"""" + str(Qval) + """ cm3/s"
phases:
    bulk:
        name: bulk
    gas:
        initial_state: "NH3:1.0"
        name: gas
    surfaces:
    -   initial_state: "RU(T):1.0"
        name: terrace
    -   initial_state: "RU(S):1.0"
        name: step
reactor:
    cat_abyv: "1500 /cm"
    temperature_mode: "isothermal"
    pressure_mode: "isobaric"
    pressure: \"""" + str(pval) + """ atm"
    temperature: """ + str(Tval) + """
    type: "cstr"
    volume: "1 cm3"
simulation:
    end_time: "100 s"
    init_step: 1.0e-15
    output_format: "csv"
    solver:
        atol: 1.0e-15
        rtol: 1.0e-10
    stepping: "logarithmic"
    transient: false
""")
    file.close()
    print(os.listdir('.'))
    subprocess.run(args=["sbatch", name + ".sq"],
                   shell=True)
    os.chdir('..')