'''
this file contains functions that help initialize the virus
parameters for the simulation
'''
# avoiding Dynamically Created Attributes:slots
# See more on https://www.python-course.eu/python3_slots.php
from virus import Virus
from stratifiedPopulation import Stratified_Population
import numpy as np


class Virus_Lethal(Virus):
    #__slots__ is an attribute you can add to a Python class when 
    # defining it: define slots with the possible attributes that 
    # an instance of an object can possess.
    
        
    __slots__ = ['__mortality_chance']
    
    # Constructor            
    def __init__(self,infection_range=0.01, infection_chance=0.02 , 
                recovery_duration=(100, 200) , mortality_chance=0.02):
        '''
    
        Keyword arguments
        -----------------
        infection_range : int
            range surrounding sick patient that infections can take place
    
        infection_chance : int
            chance that an infection spreads to nearby healthy people each tick
    
        recovery_duration : 2d array
            how many ticks it may take to recover from the illness
    
        mortality_chance : 2d array
            lower and upper bounds of x axis
        '''
        # virus properties
        self.infection_range   = infection_range 
        self.infection_chance  = infection_chance  
        self.recovery_duration = recovery_duration       
        self.mortality_chance  = mortality_chance
        
    @property
    def mortality_chance(self):
        return self.__mortality_chance

    @mortality_chance.setter
    def mortality_chance(self, v):
        if not (v > 0): raise Exception("mortality_chance must be greater than zero")
        self.__mortality_chance = v
        
    def mutate(self):
        print("This is your challenge")
        
        
    def recover_or_die(self,pop,soc,config):
        '''see whether to recover or die
    
    
        Keyword arguments
        -----------------
        population : ndarray
            array containing all data on the population
    
        frame : int
            the current timestep of the simulation
    
        recovery_duration : tuple
            lower and upper bounds of duration of recovery, in simulation steps
    
        mortality_chance : float
            the odds that someone dies in stead of recovers (between 0 and 1)
    
        risk_age : int or flaot
            the age from which mortality risk starts increasing
    
        critical_age: int or float
            the age where mortality risk equals critical_mortality_change
    
        critical_mortality_chance : float
            the heightened odds that an infected person has a fatal ending
    
        risk_increase : string
            can be 'quadratic' or 'linear', determines whether the mortality risk
            between the at risk age and the critical age increases linearly or
            exponentially
    
        no_treatment_factor : int or float
            defines a change in mortality odds if someone cannot get treatment. Can
            be larger than one to increase risk, or lower to decrease it.
    
        treatment_dependent_risk : bool
            whether availability of treatment influences patient risk
    
        treatment_factor : int or float
            defines a change in mortality odds if someone is in treatment. Can
            be larger than one to increase risk, or lower to decrease it.
    
        verbose : bool
            whether to report to terminal the recoveries and deaths for each simulation step
        '''
        population = pop.population
        #find infected people
        infected_people = population[population[:,6] == 1]
    
        #define vector of how long everyone has been sick
        illness_duration_vector = config.frame - infected_people[:,8]
        
        recovery_odds_vector = (illness_duration_vector - self.recovery_duration[0]) / np.ptp(self.recovery_duration)
        recovery_odds_vector = np.clip(recovery_odds_vector, a_min = 0, a_max = None)
    
        #update states of sick people 
        indices = infected_people[:,0][recovery_odds_vector >= infected_people[:,9]]
    
        recovered = []
        fatalities = []
    
        #decide whether to die or recover
        for idx in indices:
            #check if we want risk to be age dependent
            #if age_dependent_risk:
            
            if isinstance(pop,Stratified_Population):
                updated_mortality_chance = self.compute_mortality(infected_people[infected_people[:,0] == idx][:,7][0], 
                                                                pop.risk_age, pop.critical_age, 
                                                                pop.critical_mortality_chance, 
                                                                pop.risk_increase)
            
            else:
                updated_mortality_chance = 0
    
            if infected_people[infected_people[:,0] == int(idx)][:,10] == 0 and soc.treatment_dependent_risk:
                #if person is not in treatment, increase risk by no_treatment_factor
                updated_mortality_chance = updated_mortality_chance * soc.no_treatment_factor
            elif infected_people[infected_people[:,0] == int(idx)][:,10] == 1 and soc.treatment_dependent_risk:
                #if person is in treatment, decrease risk by 
                updated_mortality_chance = updated_mortality_chance * soc.treatment_factor
    
            if np.random.random() <= updated_mortality_chance:
                #die
                infected_people[:,6][infected_people[:,0] == idx] = 3
                infected_people[:,10][infected_people[:,0] == idx] = 0
                fatalities.append(np.int32(infected_people[infected_people[:,0] == idx][:,0][0]))
            else:
                #recover (become immune)
                infected_people[:,6][infected_people[:,0] == idx] = 2
                infected_people[:,10][infected_people[:,0] == idx] = 0
                recovered.append(np.int32(infected_people[infected_people[:,0] == idx][:,0][0]))
    
        if len(fatalities) > 0 and config.verbose:
            print('\nat timestep %i these people died: %s' %(config.frame, fatalities))
        if len(recovered) > 0 and config.verbose:
            print('\nat timestep %i these people recovered: %s' %(config.frame, recovered))
    
        #put array back into population
        population[population[:,6] == 1] = infected_people
    
        return population
    
    
    def compute_mortality(self, age, risk_age=50,
                          critical_age=80, critical_mortality_chance=0.5,
                          risk_increase='linear'):
    
        '''compute mortality based on age
    
        The risk is computed based on the age, with the risk_age marking
        the age where risk starts increasing, and the crticial age marks where
        the 'critical_mortality_odds' become the new mortality chance.
    
        Whether risk increases linearly or quadratic is settable.
    
        Keyword arguments
        -----------------
        age : int
            the age of the person
    
        mortality_chance : float
            the base mortality chance
            can be very small but cannot be zero if increase is quadratic.
    
        risk_age : int
            the age from which risk starts increasing
    
        critical_age : int
            the age where mortality risk equals the specified 
            critical_mortality_odds
    
        critical_mortality_chance : float
            the odds of dying at the critical age
    
        risk_increase : str
            defines whether the mortality risk between the at risk age
            and the critical age increases linearly or exponentially
        '''
    
        if risk_age < age < critical_age: # if age in range
            if risk_increase == 'linear':
                #find linear risk
                step_increase = (critical_mortality_chance) / ((critical_age - risk_age) + 1)
                risk = critical_mortality_chance - ((critical_age - age) * step_increase)
                return risk
            elif risk_increase == 'quadratic':
                #define exponential function between risk_age and critical_age
                pw = 15
                A = np.exp(np.log(self.mortality_chance / critical_mortality_chance)/pw)
                a = ((risk_age - 1) - critical_age * A) / (A - 1)
                b = self.mortality_chance / ((risk_age -1) + a ) ** pw
    
                #define linespace
                x = np.linspace(0, critical_age, critical_age)
                #find values
                risk_values = ((x + a) ** pw) * b
                return risk_values[np.int32(age- 1)]
        elif age <= risk_age:
            #simply return the base mortality chance
            return self.mortality_chance
        elif age >= critical_age:
            #simply return the maximum mortality chance
            return critical_mortality_chance
    

        
        