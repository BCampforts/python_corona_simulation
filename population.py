'''
this file contains functions that help initialize the population
parameters for the simulation
'''

from glob import glob
import numpy as np
from motion import get_motion_parameters, update_randoms
from utils import check_folder

class Population():
    __slots__ = ['pop_size',                  
                  'xbounds',
                  'ybounds',                  
                  'speed',
                  'wander_range',
                  'wander_factor',
                  'wander_factor_dest',
                  'population',
                  'destinations']
        
    def __init__(self, 
                 pop_size   = 500,
                 xbounds    = [0.02, 0.498], 
                 ybounds    = [0.02, 0.498],
                 #age_dependent_risk = True, #whether risk increases with age
                 speed = 0.015, #average speed of population
                 wander_range = 0.05,
                 wander_factor = 1 ,
                 wander_factor_dest = 1.5, #area around destination 
                 ):
        '''initialized the population for the simulation
    
        the population matrix for this simulation has the following columns:
    
        0 : unique ID
        1 : current x coordinate
        2 : current y coordinate
        3 : current heading in x direction
        4 : current heading in y direction
        5 : current speed
        6 : current state (0=healthy, 1=sick, 2=immune, 3=dead, 4=immune but infectious)
        7 : age
        8 : infected_since (frame the person got infected)
        9 : recovery vector (used in determining when someone recovers or dies)
        10 : in treatment
        11 : active destination (0 = random wander, 1, .. = destination matrix index)
        12 : at destination: whether arrived at destination (0=traveling, 1=arrived)
        13 : wander_range_x : wander ranges on x axis for those who are confined to a location
        14 : wander_range_y : wander ranges on y axis for those who are confined to a location
        
        
        #average speed of population
        #when people have an active destination, the wander range defines the area
        #surrounding the destination they will wander upon arriving
    
        Keyword arguments
        -----------------
        pop_size : int
            the size of the population
    
        mean_age : int
            the mean age of the population. Age affects mortality chances
    
        max_age : int
            the max age of the population
    
        xbounds : 2d array
            lower and upper bounds of x axis
    
        ybounds : 2d array
            lower and upper bounds of y axis
        '''
        
        # population properties
        #world variables, defines where population can and cannot roam
        self.xbounds = xbounds
        self.ybounds = ybounds
        self.pop_size = pop_size
        self.speed = speed
        self.wander_range = wander_range
        self.wander_factor = wander_factor 
        self.wander_factor_dest = wander_factor_dest #area around destination
    
    #initialize population matrix
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
        #initalize ages (on ly for stratified populations)
        # std_age = (self.max_age - self.mean_age) / 3
        # self.population[:,7] = np.int32(np.random.normal(loc = self.mean_age, 
        #                                             scale = std_age, 
        #                                             size=(self.pop_size,)))
        # self.population[:,7] = np.clip(self.population[:,7], a_min = 0, 
        #                           a_max = self.max_age) #clip those younger than 0 years
        #build recovery_vector
        self.population[:,9] = np.random.normal(loc = 0.5, scale = 0.5 / 3, size=(self.pop_size,))
    
        
    
    
    def initialize_destination_matrix(self, total_destinations=1):
        '''intializes the destination matrix
    
        function that initializes the destination matrix used to
        define individual location and roam zones for population members
    
        Keyword arguments
        -----------------
        pop_size : int
            the size of the population
    
        total_destinations : int
            the number of destinations to maintain in the matrix. Set to more than
            one if for example people can go to work, supermarket, home, etc.
        '''
    
        self.destinations = np.zeros((self.pop_size, total_destinations * 2))
    
        
    
    
    def set_destination_bounds(self, xmin, ymin, 
                               xmax, ymax, dest_no=1, teleport=True):
        '''teleports all persons within limits
    
        Function that takes the population and coordinates,
        teleports everyone there, sets destination active and
        destination as reached
    
        Keyword arguments
        -----------------
        population : ndarray
            the array containing all the population information
    
        destinations : ndarray
            the array containing all the destination information
    
        xmin, ymin, xmax, ymax : int or float
            define the bounds on both axes where the individual can roam within
            after reaching the defined area
    
        dest_no : int
            the destination number to set as active (if more than one)
    
        teleport : bool
            whether to instantly teleport individuals to the defined locations
        '''
    
        #teleport
        if teleport:
            self.population[:,1] = np.random.uniform(low = xmin, high = xmax, size = len(self.population))
            self.population[:,2] = np.random.uniform(low = ymin, high = ymax, size = len(self.population))
    
        #get parameters
        x_center, y_center, x_wander, y_wander = get_motion_parameters(xmin, ymin, 
                                                                       xmax, ymax)
    
        #set destination centers
        self.destinations[:,(dest_no - 1) * 2] = x_center
        self.destinations[:,((dest_no - 1) * 2) + 1] = y_center
    
        #set wander bounds
        self.population[:,13] = x_wander
        self.population[:,14] = y_wander
    
        self.population[:,11] = dest_no #set destination active
        self.population[:,12] = 1 #set destination reached
    
    
    
    def find_nearby(self, infection_zone, traveling_infects=False,
                kind='healthy', infected_previous_step=[]):
        '''finds nearby IDs
    
        Keyword Arguments
        -----------------
    
        kind : str (can be 'healthy' or 'infected')
            determines whether infected or healthy individuals are returned
            within the infection_zone
    
    
        Returns
        -------
        if kind='healthy', indices of healthy agents within the infection
        zone is returned. This is because for each healthy agent, the chance to
        become infected needs to be tested
    
        if kind='infected', only the number of infected within the infection zone is
        returned. This is because in this situation, the odds of the healthy agent at
        the center of the infection zone depend on how many infectious agents are around
        it.
        '''
        population =self.population
    
        if kind.lower() == 'healthy':
            indices = np.int32(population[:,0][(infection_zone[0] < population[:,1]) & 
                                                (population[:,1] < infection_zone[2]) &
                                                (infection_zone[1] < population [:,2]) & 
                                                (population[:,2] < infection_zone[3]) &
                                                (population[:,6] == 0)])
            return indices
    
        elif kind.lower() == 'infected':
            if traveling_infects:
                infected_number = len(infected_previous_step[:,6][(infection_zone[0] < infected_previous_step[:,1]) & 
                                                                (infected_previous_step[:,1] < infection_zone[2]) &
                                                                (infection_zone[1] < infected_previous_step [:,2]) & 
                                                                (infected_previous_step[:,2] < infection_zone[3]) &
                                                                (infected_previous_step[:,6] == 1)])
            else:
                infected_number = len(infected_previous_step[:,6][(infection_zone[0] < infected_previous_step[:,1]) & 
                                                                (infected_previous_step[:,1] < infection_zone[2]) &
                                                                (infection_zone[1] < infected_previous_step [:,2]) & 
                                                                (infected_previous_step[:,2] < infection_zone[3]) &
                                                                (infected_previous_step[:,6] == 1) &
                                                                (infected_previous_step[:,11] == 0)])
            return infected_number
            
        else:
            raise ValueError('type to find %s not understood! Must be either \'healthy\' or \'ill\'')
         
        
    
    
    
    
    '''
contains methods related to goal-directed traveling behaviour 
and path planning
'''


    def go_to_location(self,patient, destination, location_bounds, dest_no=1):
        '''sends patient to defined location
    
        Function that takes a patient an destination, and sets the location
        as active for that patient.
    
        Keyword arguments
        -----------------
        patient : 1d array
            1d array of the patient data, is a row from population matrix
    
        destination : 1d array
            1d array of the destination data, is a row from destination matrix
    
        location_bounds : list or tuple
            defines bounds for the location the patient will be roam in when sent
            there. format: [xmin, ymin, xmax, ymax]
    
        dest_no : int
            the location number, used as index for destinations array if multiple possible
            destinations are defined`.
    
    
        TODO: vectorize
    
        '''
    
        x_center, y_center, x_wander, y_wander = get_motion_parameters(location_bounds[0],
                                                                        location_bounds[1],
                                                                        location_bounds[2],
                                                                        location_bounds[3])
        patient[13] = x_wander
        patient[14] = y_wander
        
        destination[(dest_no - 1) * 2] = x_center
        destination[((dest_no - 1) * 2) + 1] = y_center
    
        patient[11] = dest_no #set destination active
    
        return patient, destination
    
    
    def set_destination(self):
        population = self.population
        destinations = self.destinations
        '''sets destination of population
    
        Sets the destination of population if destination marker is not 0.
        Updates headings and speeds as well.
    
        Keyword arguments
        -----------------
        population : ndarray
            the array containing all the population information
    
        destinations : ndarray
            the array containing all destinations information
        '''
        
        #how many destinations are active
        active_dests = np.unique(population[:,11][population[:,11] != 0])
    
        #set destination
        for d in active_dests:
            dest_x = destinations[:,int((d - 1) * 2)]
            dest_y = destinations[:,int(((d - 1) * 2) + 1)]
    
            #compute new headings
            head_x = dest_x - population[:,1]
            head_y = dest_y - population[:,2]
    
            #head_x = head_x / np.sqrt(head_x)
            #head_y = head_y / np.sqrt(head_y)
    
            #reinsert headings into population of those not at destination yet
            population[:,3][(population[:,11] == d) &
                            (population[:,12] == 0)] = head_x[(population[:,11] == d) &
                                                                (population[:,12] == 0)]
            population[:,4][(population[:,11] == d) &
                            (population[:,12] == 0)] = head_y[(population[:,11] == d) &
                                                                (population[:,12] == 0)]
            #set speed to 0.01
            population[:,5][(population[:,11] == d) &
                            (population[:,12] == 0)] = 0.02
    
        return population
    
    
    def check_at_destination(self):
        '''check who is at their destination already
    
        Takes subset of population with active destination and
        tests who is at the required coordinates. Updates at destination
        column for people at destination.    
    
        Keyword arguments
        -----------------
        population : ndarray
            the array containing all the population information
    
        destinations : ndarray
            the array containing all destinations information
    
        wander_factor : int or float
            defines how far outside of 'wander range' the destination reached
            is triggered
        '''
        
        population = self.population
        destinations = self.destinations
        wander_factor=self.wander_factor
        speed = self.speed
        
        
        #how many destinations are active
        active_dests = np.unique(population[:,11][(population[:,11] != 0)])
    
        #see who is at destination
        for d in active_dests:
            dest_x = destinations[:,int((d - 1) * 2)]
            dest_y = destinations[:,int(((d - 1) * 2) + 1)]
    
            #see who arrived at destination and filter out who already was there
            at_dest = population[(np.abs(population[:,1] - dest_x) < (population[:,13] * wander_factor)) & 
                                    (np.abs(population[:,2] - dest_y) < (population[:,14] * wander_factor)) &
                                    (population[:,12] == 0)]
    
            if len(at_dest) > 0:
                #mark those as arrived
                at_dest[:,12] = 1
                #insert random headings and speeds for those at destination
                at_dest = update_randoms(at_dest, pop_size = len(at_dest), speed = speed,
                                         heading_update_chance = 1, speed_update_chance = 1)
    
                #at_dest[:,5] = 0.001
    
                #reinsert into population
                population[(np.abs(population[:,1] - dest_x) < (population[:,13] * wander_factor)) & 
                            (np.abs(population[:,2] - dest_y) < (population[:,14] * wander_factor)) &
                            (population[:,12] == 0)] = at_dest
    
    
        return population
            
    
    def keep_at_destination(self):
        '''keeps those who have arrived, within wander range
    
        Function that keeps those who have been marked as arrived at their
        destination within their respective wander ranges
    
        Keyword arguments
        -----------------
        population : ndarray
            the array containing all the population information
    
        destinations : ndarray
            the array containing all destinations information
    
        wander_factor : int or float
            defines how far outside of 'wander range' the destination reached
            is triggered
        ''' 
        population =self.population
        destinations = self.destinations
        wander_factor =self.wander_factor
        #how many destinations are active
        active_dests = np.unique(population[:,11][(population[:,11] != 0) &
                                                    (population[:,12] == 1)])
    
        for d in active_dests:
            dest_x = destinations[:,int((d - 1) * 2)][(population[:,12] == 1) &
                                                        (population[:,11] == d)]
            dest_y = destinations[:,int(((d - 1) * 2) + 1)][(population[:,12] == 1) &
                                                            (population[:,11] == d)]
    
            #see who is marked as arrived
            arrived = population[(population[:,12] == 1) &
                                    (population[:,11] == d)]
    
            ids = np.int32(arrived[:,0]) # find unique IDs of arrived persons
            
            #check if there are those out of bounds
            #replace x oob
            #where x larger than destination + wander, AND heading wrong way, set heading negative
            shp = arrived[:,3][arrived[:,1] > (dest_x + (arrived[:,13] * wander_factor))].shape
    
            arrived[:,3][arrived[:,1] > (dest_x + (arrived[:,13] * wander_factor))] = -np.random.normal(loc = 0.5,
                                                                    scale = 0.5 / 3,
                                                                    size = shp)
    
    
            #where x smaller than destination - wander, set heading positive
            shp = arrived[:,3][arrived[:,1] < (dest_x - (arrived[:,13] * wander_factor))].shape
            arrived[:,3][arrived[:,1] < (dest_x - (arrived[:,13] * wander_factor))] = np.random.normal(loc = 0.5,
                                                                scale = 0.5 / 3,
                                                                size = shp)
            #where y larger than destination + wander, set heading negative
            shp = arrived[:,4][arrived[:,2] > (dest_y + (arrived[:,14] * wander_factor))].shape
            arrived[:,4][arrived[:,2] > (dest_y + (arrived[:,14] * wander_factor))] = -np.random.normal(loc = 0.5,
                                                                    scale = 0.5 / 3,
                                                                    size = shp)
            #where y smaller than destination - wander, set heading positive
            shp = arrived[:,4][arrived[:,2] < (dest_y - (arrived[:,14] * wander_factor))].shape
            arrived[:,4][arrived[:,2] < (dest_y - (arrived[:,14] * wander_factor))] = np.random.normal(loc = 0.5,
                                                                scale = 0.5 / 3,
                                                                size = shp)
    
            #slow speed
            arrived[:,5] = np.random.normal(loc = 0.005,
                                            scale = 0.005 / 3, 
                                            size = arrived[:,5].shape)
    
            #reinsert into population
            population[(population[:,12] == 1) &
                        (population[:,11] == d)] = arrived
                                    
        return population
    
    
    def reset_destinations(self, ids=[]):
        '''clears destination markers
    
        Function that clears all active destination markers from the population
    
        Keyword arguments
        -----------------
        population : ndarray
            the array containing all the population information
    
        ids : ndarray or list
            array containing the id's of the population members that need their
            destinations reset
        '''
        population=self.population
        
        if len(ids) == 0:
            #if ids empty, reset everyone
            population[:,11] = 0
        else:
            pass
            #else, reset id's
    
        
        pass
    def save_data(self, pop_tracker):
        '''dumps simulation data to disk
    
        Function that dumps the simulation data to specific files on the disk.
        Saves final state of the population matrix, the array of infected over time,
        and the array of fatalities over time
    
        Keyword arguments
        -----------------
        population : ndarray
            the array containing all the population information
    
        infected : list or ndarray
            the array containing data of infections over time
    
        fatalities : list or ndarray
            the array containing data of fatalities over time
        ''' 
        num_files = len(glob('data/*'))
        check_folder('data/%i' %num_files)
        np.save('data/%i/population.npy' %num_files, self.population)
        np.save('data/%i/infected.npy' %num_files, pop_tracker.infectious)
        np.save('data/%i/recovered.npy' %num_files, pop_tracker.recovered)
        np.save('data/%i/fatalities.npy' %num_files, pop_tracker.fatalities)
    
    
    def save_population(self, tstep=0, folder='data_tstep'):
        '''dumps population data at given timestep to disk
    
        Function that dumps the simulation data to specific files on the disk.
        Saves final state of the population matrix, the array of infected over time,
        and the array of fatalities over time
    
        Keyword arguments
        -----------------
        population : ndarray
            the array containing all the population information
    
        tstep : int
            the timestep that will be saved
        ''' 
        check_folder('%s/' %(folder))
        np.save('%s/population_%i.npy' %(folder, tstep), self.population)
        
        
    def set_reduced_interaction(self, speed = 0.001):
        '''sets reduced interaction scenario to active'''

        self.speed = speed
    
    
