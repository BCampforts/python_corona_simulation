# %matplotlib

import os
import sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from config import Configuration
from environment import build_hospital
from motion import update_positions, out_of_bounds, update_randoms,\
get_motion_parameters
from population import Population
from tracker import Population_trackers
from visualiser import build_fig, draw_tstep, set_style

#set seed for reproducibility
np.random.seed(100)


   


    
def tstep(config,vir,pop,pop_tracker,soc, fig, spec, ax1, ax2 ):
    '''
    takes a time step in the simulation
    '''

    #check destinations if active
    #define motion vectors if destinations active and not everybody is at destination
    active_dests = len(pop.population[pop.population[:,11] != 0]) # look op this only once

    if active_dests > 0 and len(pop.population[pop.population[:,12] == 0]) > 0:
        pop.population = pop.set_destination()
        pop.population = pop.check_at_destination()

    if active_dests > 0 and len(pop.population[pop.population[:,12] == 1]) > 0:
        #keep them at destination
        pop.population = pop.keep_at_destination()

    #out of bounds
    #define bounds arrays, excluding those who are marked as having a custom destination
    if len(pop.population[:,11] == 0) > 0:
        _xbounds = np.array([[config.xbounds[0] + 0.02, config.xbounds[1] - 0.02]] * len(pop.population[pop.population[:,11] == 0]))
        _ybounds = np.array([[config.ybounds[0] + 0.02, config.ybounds[1] - 0.02]] * len(pop.population[pop.population[:,11] == 0]))
        pop.population[pop.population[:,11] == 0] = out_of_bounds(pop.population[pop.population[:,11] == 0], 
                                                                    _xbounds, _ybounds)
    
    #set randoms
    if soc.lockdown:
        if len(pop_tracker.infectious) == 0:
            mx = 0                
        else:
            #mx = np.max(pop_tracker.infectious)
            mx = pop_tracker.infectious[-1]  
            
        if len(pop.population[pop.population[:,6] == 1]) >= len(pop.population) * soc.lockdown_percentage or\
           mx >= (len(pop.population) * soc.lockdown_percentage) or soc.lockdown_act:
            soc.lockdown_act =True
            #reduce speed of all members of society
            pop.population[:,5] = np.clip(pop.population[:,5], a_min = None, a_max = 0.00001)
            #set speeds of complying people to 0
            pop.population[:,5][soc.lockdown_vector == 0] = 0
            if len(pop.population[pop.population[:,6] == 1]) <= len(pop.population) * soc.lockdown_percentage/2:
                soc.lockdown_act = False
        else:
            #update randoms
            pop.population = update_randoms(pop.population, pop.pop_size, pop.speed)
    else:
        #update randoms
        pop.population = update_randoms(pop.population, pop.pop_size, pop.speed)

    #for dead ones: set speed and heading to 0
    pop.population[:,3:5][pop.population[:,6] == 3] = 0
    
    #update positions
    pop.population = update_positions(pop.population)

    #find new infections
    pop.population, pop.destinations = vir.infect(pop,soc,config,
                                              send_to_location = soc.self_isolate, 
                                              location_bounds = soc.isolation_bounds,  
                                              destinations = pop.destinations, 
                                              location_no = 1, 
                                              location_odds = soc.self_isolate_proportion)

    #recover and die
    pop.population = vir.recover_or_die(pop,soc,config)

    #send cured back to population if self isolation active
    #perhaps put in recover or die class
    #send cured back to population
    pop.population[:,11][pop.population[:,6] == 2] = 0

    #update population statistics
    pop_tracker.update_counts(pop.population)

    #visualise
    if config.visualise:
        draw_tstep(config, soc, pop.pop_size, pop.population, pop_tracker, config.frame, 
                   fig, spec, ax1, ax2)

    #report stuff to console
    sys.stdout.write('\r')
    sys.stdout.write('%i: healthy: %i, infected: %i, immune: %i, in treatment: %i, \
dead: %i, of total: %i' %(config.frame, pop_tracker.susceptible[-1], pop_tracker.infectious[-1],
                    pop_tracker.recovered[-1], len(pop.population[pop.population[:,10] == 1]),
                    pop_tracker.fatalities[-1], pop.pop_size))

    #save popdata if required
    if config.save_pop and (config.frame % config.save_pop_freq) == 0:
        pop.save_population(pop.population, config.frame, config.save_pop_folder)
    #run callback
    callback(pop,config)

    #update frame
    config.frame += 1


def callback(pop,config):
    '''placeholder function that can be overwritten.

    By ovewriting this method any custom behaviour can be implemented.
    The method is called after every simulation timestep.
    '''

    if config.frame == 1:
        print('\ninfecting person')
        pop.population[0][6] = 1
        pop.population[0][8] = 50
        pop.population[0][10] = 1
        
        pop.population[1][6] = 1
        pop.population[1][8] = 20
        pop.population[1][10] = 1


def run(config,vir,pop,pop_tracker,soc, fig, spec, ax1, ax2 ):
    '''run simulation'''

    i = 0
    
    while i < config.simulation_steps:
        try:
            tstep(config,vir,pop,pop_tracker,soc, fig, spec, ax1, ax2 )
        except KeyboardInterrupt:
            print('\nCTRL-C caught, exiting')
            sys.exit(1)

        #check whether to end if no infecious persons remain.
        #check if self.frame is above some threshold to prevent early breaking when simulation
        #starts initially with no infections.
        if config.endif_no_infections and config.frame >= 500:
            if len(pop.population[(pop.population[:,6] == 1) | 
                                   (pop.population[:,6] == 4)]) == 0:
                i = config.simulation_steps

    if config.save_data:
        pop.save_data(pop_tracker)

    #report outcomes
    print('\n-----stopping-----\n')
    print('total timesteps taken: %i' %config.frame)
    population = pop.population
    print('total dead: %i' %len(population[population[:,6] == 3]))
    print('total recovered: %i' %len(population[population[:,6] == 2]))
    print('total infected: %i' %len(population[population[:,6] == 1]))
    print('total infectious: %i' %len(population[(population[:,6] == 1) |
                                                      (population[:,6] == 4)]))
    print('total unaffected: %i' %len(population[population[:,6] == 0]))



