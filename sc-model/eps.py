import numpy as np
import constants as C
propulsion = 'chemical'


case = 1

###Spacecraft Power 

ADCSpower = 304 # [W]
OBDHpower = 1.5 # 0.5-1.5 [W]
COMMpower_data = 30 # 20-30 [W]
COMMpower_telemetry = 10 # 20-30 [W]
PROPpower = 2 # Margin, we don't know. [W]
TCpower = 172.21 # with 6% margin [W]
STRUCpower = 10 # [W]

#payloads
HSRC_a = 45.7
HSRC_i = 6
UVS = 9.7
MAG = 4
Laser_a = 25
Laser_i = 2 

PAYpower = HSRC_a + HSRC_i + UVS + MAG + Laser_a + Laser_i # [W]

###Mission Charachteristics

TRANSFER_DURATION = None   # s
MAX_ECLIPSE_DURATION = 2115.2 # s
EARTH_OCCULTATION = 2118
ORBITAL_PERIOD = 7630 #s
SUNLIGHT_DURATION = ORBITAL_PERIOD - MAX_ECLIPSE_DURATION # s, available recharge time per orbit
DATA_TRANS_PERIOD = ORBITAL_PERIOD - EARTH_OCCULTATION

POWER_SCIENCE = None       
POWER_HIBERNATION = None   
POWER_DATA_TRANSM = None       
POWER_PEAK = PAYpower + ADCSpower + OBDHpower + COMMpower_data + PROPpower + TCpower + STRUCpower           # W, maximum simultaneous load

# ---------- Power management / distribution ----------
ARRAY_TO_BUS_EFF = 0.9     # fraction
BUS_TO_LOAD_EFF = 0.9      # fraction
BATTERY_TO_BUS_EFF = 0.9   # fraction; converter/path losses only
BUS_TO_BATTERY_EFF = 0.9   # fraction; converter/path losses only
PMAD_MASS = None            # kg, initial estimate or component sum


# ---------- Design assumptions----------
POWER_MARGIN = 0.20      # 
MASS_MARGIN = 0.20         # 


### RTG ##

RTG_SPEC_POWER =  2.4 # W/kg
RTG_SPEC_COST = 7.3e-6 # W / EUR


# ---------- Solar-array inputs: from selected cell/array data ----------
CELL_EFFICIENCY_REF = 0.3  # fraction, at reference temperature
CELL_REFERENCE_TEMP = 301.15 # K
POWER_TEMP_COEFF = -0.0025     # 1/K, relative coefficient; usually negative
CELL_OPERATING_TEMP = 420  # K

ARRAY_EOL_FACTOR = 0.75    # fraction of initial performance remaining
ARRAY_PACKING_FACTOR = 0.9 # active cell area / total panel area
SUN_INCIDENCE_ANGLE = 0.5  # rad, measured FROM THE PANEL NORMAL

ARRAY_AREAL_MASS = 2     # kg/m²; document included hardware


# ---------- Battery inputs: from selected battery data ----------
BATTERY_SPECIFIC_ENERGY = 200 # 160-300 Wh/kg; preferably pack-level
BATTERY_ENERGY_DENSITY = 500  #250-842 Wh/L; preferably pack-level
BATTERY_MAX_DOD = 0.9         # fraction, allowed depth of discharge, degrades with life
BATTERY_EOL_CAPACITY = 0.8    # remaining capacity / initial capacity

BATTERY_CHARGE_EFF = 0.8      # fraction
BATTERY_DISCHARGE_EFF = 0.8   # fraction
BATTERY_SPECIFIC_COST = 108 # Dollar per kw
BATTERY_CYCLE_DURABILITY = 600 # 400 - 1200 cycles 


## WE NEED TO CALCULATE: MASS SIZE BATTERIES MASS SIZE SOLAR PANELS mass size RTG
##CASE 1 (SOLAR):

if case == 1:

    ORBIT_ENERGY = (
        
        (HSRC_a * 0.2 *ORBITAL_PERIOD + HSRC_i * 0.8 * ORBITAL_PERIOD + UVS *0.25 * ORBITAL_PERIOD + MAG * ORBITAL_PERIOD + Laser_a * MAX_ECLIPSE_DURATION + Laser_i * SUNLIGHT_DURATION) +
        PROPpower * 0 + OBDHpower * ORBITAL_PERIOD + COMMpower_data * DATA_TRANS_PERIOD + ADCSpower *ORBITAL_PERIOD + TCpower * ORBITAL_PERIOD +STRUCpower * 0
    ) * (1+POWER_MARGIN) # [j]
    ORBITAL_POWER = ORBIT_ENERGY / SUNLIGHT_DURATION

    # Size at Mercury aphelion: lowest solar flux -> worst case for array area
    SOLAR_FLUX = C.SOLAR_FLUX_1AU * (C.AU / C.MERCURY_APHELION)**2  # [W/m²]
    TEMP_FACTOR = 1 + POWER_TEMP_COEFF * (CELL_OPERATING_TEMP - CELL_REFERENCE_TEMP)

    # EOL power produced per m² of panel
    ARRAY_POWER_DENSITY = (
        SOLAR_FLUX * CELL_EFFICIENCY_REF * TEMP_FACTOR * ARRAY_PACKING_FACTOR
        * np.cos(SUN_INCIDENCE_ANGLE) * ARRAY_EOL_FACTOR
    )  # [W/m²]

    # Array must also cover distribution losses between array and loads
    ARRAY_POWER_REQ = ORBITAL_POWER / (ARRAY_TO_BUS_EFF * BUS_TO_LOAD_EFF)  # [W]

    SOLAR_ARRAY_SIZE = ARRAY_POWER_REQ / ARRAY_POWER_DENSITY  # [m²]
    SOLAR_ARRAY_MASS = SOLAR_ARRAY_SIZE * ARRAY_AREAL_MASS    # [kg]


print(ORBIT_ENERGY, ORBITAL_POWER, SOLAR_ARRAY_SIZE, SOLAR_ARRAY_MASS)
##CASE 2 (SOLAR + RTG):