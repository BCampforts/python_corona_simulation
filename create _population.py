#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 18:42:28 2020

@author: beca4397
"""

from population import Population
from stratifiedPopulation import Stratified_Population
import matplotlib
import matplotlib.pyplot as plt
matplotlib.rcParams["font.size"] = 20
matplotlib.rcParams["pdf.fonttype"] = 42

plt.close("all")



pop1 = Population()
pop1.initialize_population_matrix()
pp1 = pop1.population

pop2 = Stratified_Population(mean_age   = 60)
# pop2.meanAge = 50
pop2.initialize_population_matrix()
pp2 = pop2.population


plt.hist(pp2[:,7])


