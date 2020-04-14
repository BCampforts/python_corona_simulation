'''
file that contains all configuration of the actual model run 
'''


class Configuration():
    
    __slots__ = [
         #simulation variables
        'verbose',#whether to print infections, recoveries and fatalities to the terminal
        'simulation_steps',#total simulation steps performed
        'tstep',#current simulation timestep
        'save_data',#whether to dump data at end of simulation
        'save_pop', #whether to save population matrix every 'save_pop_freq' timesteps
        'save_pop_freq', #population data will be saved every 'n' timesteps. Default: 10
        'save_pop_folder',#folder to write population timestep data to
        'endif_no_infections' ,#whether to stop simulation if no infections remain             

        #world variables, defines where population can and cannot roam
        'xbounds', 
        'ybounds' ,
        
        #visualisation variables
        'visualise' , #whether to visualise the simulation 
        'plot_mode' , #default or sir
        #size of the simulated world in coordinates
        'x_plot' ,
        'y_plot',
        'save_plot',
        'plot_path' ,#folder where plots are saved to
        'plot_style' ,#can be default, dark, ...
        'colorblind_mode',
        #if colorblind is enabled, set type of colorblindness
        #available: deuteranopia, protanopia, tritanopia. defauld=deuteranopia
        'colorblind_type',
        'frame']
    
    def __init__(self, 
        verbose = True, 
        simulation_steps = 10000, 
        tstep = 0, 
        save_data = False, 
        save_pop = False, 
        save_pop_freq = 10, 
        save_pop_folder = 'pop_data/' ,
        endif_no_infections = True, 
        xbounds = [0.02, 0.498],
        ybounds = [0.02, 0.498],
        visualise = True ,
        plot_mode = 'sir', 
        x_plot = [0.02, .498] ,
        y_plot = [0.02, .498],
        save_plot = False,
        plot_path = 'render/' ,
        plot_style = 'default' ,
        colorblind_mode = False,
        colorblind_type = 'deuteranopia',
        frame = 0):
        
        
        #simulation variables
        self.verbose = verbose 
        self.simulation_steps = simulation_steps 
        self.tstep = tstep
        self.save_data = save_data 
        self.save_pop = save_pop 
        self.save_pop_freq = save_pop_freq
        self.save_pop_folder = save_pop_folder
        self.endif_no_infections =endif_no_infections 

        self.xbounds = xbounds
        self.ybounds = ybounds
        self.visualise = visualise
        self.plot_mode = plot_mode
        self.x_plot = x_plot
        self.y_plot =y_plot
        self.save_plot = save_plot
        self.plot_path = plot_path
        self.plot_style = plot_style
        self.colorblind_mode = colorblind_mode
        self.colorblind_type = colorblind_type
        self.frame = frame
        
        
    def get_palette(self):
        '''returns appropriate color palette

        Uses config.plot_style to determine which palette to pick, 
        and changes palette to colorblind mode (config.colorblind_mode)
        and colorblind type (config.colorblind_type) if required.

        Palette colors are based on
        https://venngage.com/blog/color-blind-friendly-palette/
        '''

        #palette colors are: [healthy, infected, immune, dead]
        palettes = {'regular': {'default': ['gray', 'red', 'green', 'black'],
                                'dark': ['#404040', '#ff0000', '#00ff00', '#000000']},
                    'deuteranopia': {'default': ['gray', '#a50f15', '#08519c', 'black'],
                                     'dark': ['#404040', '#fcae91', '#6baed6', '#000000']},
                    'protanopia': {'default': ['gray', '#a50f15', '08519c', 'black'],
                                   'dark': ['#404040', '#fcae91', '#6baed6', '#000000']},
                    'tritanopia': {'default': ['gray', '#a50f15', '08519c', 'black'],
                                   'dark': ['#404040', '#fcae91', '#6baed6', '#000000']}
                    }

        if self.colorblind_mode:
            return palettes[self.colorblind_type.lower()][self.plot_style]
        else:
            return palettes['regular'][self.plot_style]



  

