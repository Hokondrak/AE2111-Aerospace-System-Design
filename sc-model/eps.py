import numpy as np
import constants as C
propulsion = 'chemical'


case = 1

###Spacecraft Power 

ADCSpower = 304 # [W]
OBDHpower = 1.5 # 0.5-1.5 [W]
COMMpower = 30 # 20-30 [W]
PROPpower = 2 # Margin, we don't know. [W]
TCpower = 172.21 # with 6% margin [W]
STRUCpower = 10 # [W]
PAYpower = 84.4 # W Maximum operation

###Mission Charachteristics

TRANSFER_DURATION = None   # s
MAX_ECLIPSE_DURATION = 2115.2 # s
ORBITAL_PERIOD = 7630 #s
SUNLIGHT_DURATION = ORBITAL_PERIOD - MAX_ECLIPSE_DURATION # s, available recharge time per orbit

POWER_SCIENCE = None       
POWER_HIBERNATION = None   
POWER_DATA_TRANSM = None       
POWER_PEAK = PAYpower + ADCSpower + OBDHpower + COMMpower + PROPpower + TCpower + STRUCpower           # W, maximum simultaneous load

# ---------- Power management / distribution ----------
ARRAY_TO_BUS_EFF = 0.9     # fraction
BUS_TO_LOAD_EFF = 0.9      # fraction
BATTERY_TO_BUS_EFF = 0.9   # fraction; converter/path losses only
BUS_TO_BATTERY_EFF = 0.9   # fraction; converter/path losses only
PMAD_MASS = None            # kg, initial estimate or component sum


# ---------- Design assumptions: illustrative----------
POWER_MARGIN = 0.20        # 
MASS_MARGIN = 0.20         # 


# ---------- Solar-array inputs: from selected cell/array data ----------
CELL_EFFICIENCY_REF = 0.3  # fraction, at reference temperature
CELL_REFERENCE_TEMP = None # K
POWER_TEMP_COEFF = None     # 1/K, relative coefficient; usually negative
CELL_OPERATING_TEMP = None  # K

ARRAY_EOL_FACTOR = 0.75    # fraction of initial performance remaining
ARRAY_PACKING_FACTOR = 0.9 # active cell area / total panel area
SUN_INCIDENCE_ANGLE = 0.5  # rad, measured FROM THE PANEL NORMAL

ARRAY_AREAL_MASS = None     # kg/m²; document included hardware


# ---------- Battery inputs: from selected battery data ----------
BATTERY_SPECIFIC_ENERGY = 200 # 160-300 Wh/kg; preferably pack-level
BATTERY_ENERGY_DENSITY = 500  #250-842 Wh/L; preferably pack-level
BATTERY_MAX_DOD = 0.9         # fraction, allowed depth of discharge, degrades with life
BATTERY_EOL_CAPACITY = 0.8    # remaining capacity / initial capacity

BATTERY_CHARGE_EFF = 0.8      # fraction
BATTERY_DISCHARGE_EFF = 0.8   # fraction
BATTERY_SPECIFIC_COST = 108 # Dollar per kw
BATTERY_CYCLE_DURABILITY = 600 # 400 - 1200 cycles 


## WE NEED TO CALCULATE: MASS SIZE BATTERIES MASS SIZE SOLAR PANELS
##CASE 1:

if case == 1:
