'''
this file contains functions that help initialize the population
parameters for the simulation
'''

import numpy as np

from population import Population

class Stratified_Population(Population):
    __slots__ = [
        'mean_age',
        'max_age',
        'age_dependent_risk',
        'risk_age',
        'critical_age',
        'critical_mortality_chance',
        'risk_increase',
        ]
        
    def __init__(self, 
                 pop_size   = 500,
                 xbounds    = [0.02, 0.498], 
                 ybounds    = [0.02, 0.498],
                 speed = 0.015, #average speed of population
                 wander_range = 0.05,
                 wander_factor = 1 ,
                 wander_factor_dest = 1.5, #area around destination 
                 mean_age   = 45, 
                 max_age    = 105,  
                 risk_age   = 55, #age where mortality risk starts increasing
                 critical_age = 75, #age at and beyond which mortality risk reaches maximum
                 critical_mortality_chance = 0.2, #maximum mortality risk for older age
                 risk_increase = 'quadratic', #whether risk between risk and critical age increases 'linear' or 'quadratic'
                 ):
        # Super class
        self.xbounds = xbounds
        self.ybounds = ybounds
        self.pop_size = pop_size
        self.speed = speed
        self.wander_range = wander_range
        self.wander_factor = wander_factor 
        self.wander_factor_dest = wander_factor_dest 
        
        # Actual class
        self.mean_age = mean_age         
        self.max_age = max_age 
        self.risk_age = risk_age #age where mortality risk starts increasing
        self.critical_age = critical_age #age at and beyond which mortality risk reaches maximum
        self.critical_mortality_chance = critical_mortality_chance #maximum mortality risk for older age
        self.risk_increase = risk_increase #whether risk between risk and critical age increases 'linear' or 'quadratic'
        
        
    #Overwrite initialize_population_matrix function 
    def initialize_population_matrix(self):
        self.population = np.zeros((self.pop_size, 15))
        #initalize unique IDs
        self.population[:,0] = [x for x in range(self.pop_size)]
        #initialize random coordinates
        self.population[:,1] = np.random.uniform(low = self.xbounds[0] + 0.05, high = self.xbounds[1] - 0.05, 
                                            size = (self.pop_size,))
        self.population[:,2] = np.random.uniform(low = self.ybounds[0] + 0.05, high = self.ybounds[1] - 0.05, 
                                            size=(self.pop_size,))
        #initialize random headings -1 to 1
        self.population[:,3] = np.random.normal(loc = 0, scale = 1/3, 
                                           size=(self.pop_size,))
        self.population[:,4] = np.random.normal(loc = 0, scale = 1/3, 
                                           size=(self.pop_size,))
        #initialize random speeds
        self.population[:,5] = np.random.normal(self.speed, self.speed / 3)
        #initalize ages
        std_age = (self.max_age - self.mean_age) / 3
        self.population[:,7] = np.int32(np.random.normal(loc = self.mean_age, 
                                                    scale = std_age, 
                                                    size=(self.pop_size,)))
        self.population[:,7] = np.clip(self.population[:,7], a_min = 0, 
                                  a_max = self.max_age) #clip those younger than 0 years
        #build recovery_vector
        self.population[:,9] = np.random.normal(loc = 0.5, scale = 0.5 / 3, size=(self.pop_size,))
    
        
    
    
    
    
    
