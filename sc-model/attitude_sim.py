##Imports

import numpy as np
import scipy.integrate as sp
import spacecraft as sc
import torques as tq  

######Functions

#two effects that change where the s/c points:
#the orbit around the planet itself
#the disturbances,
#which turn on and off at every time
#so the flow would be:
#for each position in orbit: Current angle, position -> Current Torques -> Current alpha -> current omega -> new position
#use euler first, then do rk6.


######