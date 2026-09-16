import numpy as np
import constants.py as C
propulsion = 'chemical'


ADCSpower = 304 # [W]
OBDHpower = 1.5 # 0.5-1.5 [W]
COMMpower = 30 # 20-30 [W]
PROPpower = 0 # [W]
##CASE 1: Chemical Propulsion
if propulsion == 'checmical':



###CASE 2: Electrical Propulsion

if propulsion == 'electrical':
    PROPpower = 10000 # [W]
