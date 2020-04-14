#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 23:23:35 2020

@author: beca4397
"""

from IPython import get_ipython
get_ipython().magic('reset -sf') 
get_ipython().magic('matplotlib auto') 

from config import Configuration 
from population import Population
from stratifiedPopulation import Stratified_Population
from society import Society
from virus import Virus
from virusLethal import Virus_Lethal
from tracker import Population_trackers
from visualiser import build_fig
from simulation import run 

# vir = Virus()
vir = Virus_Lethal()


# pop = Population()
pop = Stratified_Population(mean_age=45, pop_size = 1000)
# pop = Stratified_Population(mean_age=45, pop_size = 1000)

# pop.initialize_population_matrix()

soc = Society()
# soc = Society(self_isolate = True,self_isolate_proportion = .95, traveling_infects =False)
soc = Society(lockdown = True, lockdown_compliance = 0.95, lockdown_percentage = 0.05)

#initalise destinations vector
pop.initialize_destination_matrix(total_destinations=1)

config = Configuration(simulation_steps = 20000)
fig, spec, ax1, ax2 = build_fig(config,pop,figsize=(10,14))

pop.initialize_population_matrix()
pop_tracker = Population_trackers()

run(config,vir,pop,pop_tracker,soc, fig, spec, ax1, ax2 )