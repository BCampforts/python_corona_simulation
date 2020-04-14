'''
this file contains functions that help initialize the virus
parameters for the simulation
'''
# avoiding Dynamically Created Attributes:slots
# See more on https://www.python-course.eu/python3_slots.php

import numpy as np
from stratifiedPopulation import Stratified_Population


class Virus():
    #__slots__ is an attribute you can add to a Python class when 
    # defining it: define slots with the possible attributes that 
    # an instance of an object can possess.    
        
    __slots__ = ['infection_range', 'infection_chance',\
                  'recovery_duration']
    
    # Constructor            
    def __init__(self,infection_range=0.01, infection_chance=0.02 , 
                recovery_duration=(100, 200)):
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
        

    def infect(self,pop,soc,config, 
               send_to_location=False,location_bounds=[], 
               destinations=[], location_no=1,location_odds=1.0):
        '''finds new infections.
        
        Function that finds new infections in an area around infected persons
        defined by infection_range, and infects others with chance infection_chance
        
        Keyword arguments
        -----------------
        population : ndarray
            array containing all data on the population
    
        pop_size : int
            the number if individuals in the population
        
        infection_range : float
            the radius around each infected person where transmission of vir can take place
    
        infection_chance : float
            the odds that the vir infects someone within range (range 0 to 1)
    
        frame : int
            the current timestep of the simulation
    
        healthcare_capacity : int
            the number of places available in the healthcare system
    
        verbose : bool
            whether to report illness events
    
        send_to_location : bool
            whether to give infected people a destination
    
        location_bounds : list
            the location bounds where the infected person is sent to and can roam
            within (xmin, ymin, xmax, ymax)
    
        destinations : list or ndarray
            the destinations vector containing destinations for each individual in the population.
            Needs to be of same length as population
    
        location_no : int
            the location number, used as index for destinations array if multiple possible
            destinations are defined
    
        location_odds: float
            the odds that someone goes to a location or not. Can be used to simulate non-compliance
            to for example self-isolation.
    
        traveling_infects : bool
            whether infected people heading to a destination can still infect others on the way there
        '''
        population = pop.population
        
        #mark those already infected first
        infected_previous_step = population[population[:,6] == 1]
        healthy_previous_step = population[population[:,6] == 0]
    
        new_infections = []
    
        #if less than half are infected, slice based on infected (to speed up computation)
        if len(infected_previous_step) < (pop.pop_size // 2):
            for patient in infected_previous_step:
                #define infection zone for patient
                infection_zone = [patient[1] - self.infection_range, patient[2] - self.infection_range,
                                    patient[1] + self.infection_range, patient[2] + self.infection_range]
    
                #find healthy people surrounding infected patient
                if soc.traveling_infects or patient[11] == 0:
                    indices = pop.find_nearby(infection_zone, kind = 'healthy')
                else:
                    indices = []
    
                for idx in indices:
                    #roll die to see if healthy person will be infected
                    if np.random.random() < self.infection_chance:
                        population[idx][6] = 1
                        population[idx][8] = config.frame
                        if len(population[population[:,10] == 1]) <= soc.healthcare_capacity:
                            population[idx][10] = 1
                            if send_to_location:
                                #send to location if die roll is positive
                                if np.random.uniform() <= location_odds:
                                    population[idx],\
                                    destinations[idx] = pop.go_to_location(population[idx],
                                                                       destinations[idx],
                                                                       location_bounds, 
                                                                       dest_no=location_no)
                            else:
                                pass
                        new_infections.append(idx)
    
        else:
            #if more than half are infected slice based in healthy people (to speed up computation)
                
            
            
            for person in healthy_previous_step:
                #define infecftion range around healthy person
                infection_zone = [person[1] - self.infection_range, person[2] - self.infection_range,
                                    person[1] + self.infection_range, person[2] + self.infection_range]
    
                if person[6] == 0: #if person is not already infected, find if infected are nearby
                    #find infected nearby healthy person
                    if soc.traveling_infects:
                        poplen = pop.find_nearby(infection_zone, 
                                             traveling_infects = True,
                                             kind = 'infected')
                    else:
                        poplen = pop.find_nearby(infection_zone, 
                                             traveling_infects = True,
                                             kind = 'infected',
                                             infected_previous_step = infected_previous_step)
                    
                    if poplen > 0:
                        if np.random.random() < (self.infection_chance * poplen):
                            #roll die to see if healthy person will be infected
                            population[np.int32(person[0])][6] = 1
                            population[np.int32(person[0])][8] = config.frame
                            if len(population[population[:,10] == 1]) <= soc.healthcare_capacity:
                                population[np.int32(person[0])][10] = 1
                                if send_to_location:
                                    #send to location and add to treatment if die roll is positive
                                    if np.random.uniform() < location_odds:
                                        population[np.int32(person[0])],\
                                        destinations[np.int32(person[0])] = pop.go_to_location(population[np.int32(person[0])],
                                                                                            destinations[np.int32(person[0])],
                                                                                            location_bounds, 
                                                                                            dest_no=location_no)
    
    
                            new_infections.append(np.int32(person[0]))
    
        if len(new_infections) > 0 and config.verbose:
            print('\nat timestep %i these people got sick: %s' %(config.frame, new_infections))
    
        if len(destinations) == 0:
            return population
        else:
            return population, destinations
    
    
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
            #Non-lethal virus
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