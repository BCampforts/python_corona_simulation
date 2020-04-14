'''
this file contains functions that help initialize the population
parameters for the simulation
'''
import numpy as np

class Society():
    __slots__ = ['self_isolate',
                 'traveling_infects',
                 'lockdown',                  
                 'lockdown_act',
                 'lockdown_percentage',
                 'lockdown_compliance',
                 'lockdown_vector',
                 'healthcare_capacity',
                 'treatment_factor',
                 'no_treatment_factor',
                 'treatment_dependent_risk',
                 'self_isolate_proportion',
                 'isolation_bounds']
        
    def __init__(self,                     
                
                self_isolate = False,
                traveling_infects = False,
                
                lockdown = False,
                lockdown_act = False,                
                lockdown_compliance = 0.95 ,#fraction of the population that will obey the lockdown   
                lockdown_percentage = 0.1 ,
                lockdown_vector =[],
                
                #healthcare variables
                healthcare_capacity = 175, #capacity of the healthcare system
                treatment_factor = 0.5, #when in treatment, affect risk by this factor
                no_treatment_factor = 6, #risk increase factor to use if healthcare system is full
                #risk parameters
                treatment_dependent_risk = True, #whether risk is affected by treatment
        
                #self isolation variables
                self_isolate_proportion = 0.6,
                isolation_bounds = [0.02, 0.02, 0.1, 0.98],                
                 ):
        
        '''
        '''
        
        # properties
        self.traveling_infects = traveling_infects
        self.self_isolate = self_isolate
        
        self.lockdown = lockdown
        self.lockdown_act = lockdown_act
        self.lockdown_percentage = lockdown_percentage
        self.lockdown_compliance = lockdown_compliance
        self.lockdown_vector = lockdown_vector
        
        #healthcare variables
        self.healthcare_capacity = healthcare_capacity
        self.treatment_factor = treatment_factor
        self.no_treatment_factor = no_treatment_factor
        #risk parameters
        self.treatment_dependent_risk = treatment_dependent_risk

        #self isolation variables
        self.self_isolate_proportion = self_isolate_proportion
        self.isolation_bounds = isolation_bounds    
    
    def set_lockdown(self, pop, lockdown_percentage=0.1, lockdown_compliance=0.9):
        '''sets lockdown to active'''
        self.lockdown = True
        #fraction of the population that will obey the lockdown
        self.lockdown_percentage = lockdown_percentage
        self.lockdown_vector = np.zeros((pop.pop_size,))
        #lockdown vector is 1 for those not complying
        self.lockdown_vector[np.random.uniform(size=(pop.pop_size,)) >= lockdown_compliance] = 1


    def set_self_isolation(self, config, self_isolate_proportion=0.9,
                           isolation_bounds = [0.02, 0.02, 0.09, 0.98],
                           xbounds = [0.12, 0.498],
                           ybounds = [0.02, 0.498],
                           x_plot = [0, 0.498],
                           y_plot = [0, 0.498],
                           traveling_infects=False):
        
        '''sets self-isolation scenario to active'''
        self.self_isolate = True
        self.isolation_bounds = isolation_bounds
        self.self_isolate_proportion = self_isolate_proportion
        #set roaming bounds to outside isolated area
        config.xbounds = xbounds
        config.ybounds = ybounds
        #update plot bounds everything is shown
        config.x_plot = x_plot
        config.y_plot = y_plot
        #update whether traveling agents also infect
        self.traveling_infects = traveling_infects
        
        
     

    
