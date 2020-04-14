#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 18:42:28 2020

@author: beca4397
"""

from virus import Virus
from virusLethal import Virus_Lethal

vir1 = Virus()
    
vir.recoveryDuration = 3
# vir.__dict__
# annot add or remove attributes from this class’ instances
# + quick and easy way to speed up your Python code (faster getting and setting and reduced memory usage) 


                
vir2 = Virus(infection_range=0.01, 
            infection_chance=0.02 ,
            recovery_duration=(100, 200))


vir3 = Virus(recovery_duration=(100,200))


# Instance from lethal corona virus
SARS_COV2 = Virus_Lethal(mortality_chance=0.02)

# Now, let quickly look into property validation, that is to validate 
# attributes of an instance of class
# e.g. mortality_chance must be greater than zero

# To do this we will use decorators 

# Okey, now, can you create a property validation method for the recovery_duration? 

