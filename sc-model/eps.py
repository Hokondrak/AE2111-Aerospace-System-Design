import numpy as np
import constants as C
propulsion = 'chemical'



###Spacecraft Power 

ADCSpower = 304 # [W]
OBDHpower = 1.5 # 0.5-1.5 [W]
COMMpower_data = 100 # 20-30 [W]
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

TRANSFER_DURATION = 6.7 * C.YEAR   # s
MAX_ECLIPSE_DURATION = 2115.2 # s
EARTH_OCCULTATION = 2118
ORBITAL_PERIOD = 7630 #s
SUNLIGHT_DURATION = ORBITAL_PERIOD - MAX_ECLIPSE_DURATION # s, available recharge time per orbit
DATA_TRANS_PERIOD = ORBITAL_PERIOD - EARTH_OCCULTATION

POWER_SCIENCE = None       
POWER_HIBERNATION = OBDHpower + COMMpower_telemetry + TCpower  # W, cruise: payload, ADCS wheels & data comms off
POWER_DATA_TRANSM = None       
POWER_PEAK = PAYpower + ADCSpower + OBDHpower + COMMpower_data + PROPpower + TCpower + STRUCpower           # W, maximum simultaneous load

# ---------- Power management / distribution ----------
ARRAY_TO_BUS_EFF = 0.9     # fraction
BUS_TO_LOAD_EFF = 0.9      # fraction
BATTERY_TO_BUS_EFF = 0.9   # fraction; converter/path losses only
BUS_TO_BATTERY_EFF = 0.9   # fraction; converter/path losses only
PMAD_MASS = 10            # kg, initial estimate or component sum
PMAD_SPECIFIC_COST = 100e3  # EUR/kg, ROUGH placeholder for space-grade power electronics


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
ARRAY_SPECIFIC_COST = 350e3  # EUR/m², ROUGH placeholder (~1000 EUR/W at 1 AU for 30% cells)


# ---------- Battery inputs: from selected battery data ----------
BATTERY_SPECIFIC_ENERGY = 200 # 160-300 Wh/kg; preferably pack-level
BATTERY_ENERGY_DENSITY = 500  #250-842 Wh/L; preferably pack-level
BATTERY_MAX_DOD = 0.5         # fraction, allowed depth of discharge, degrades with life
BATTERY_EOL_CAPACITY = 0.8    # remaining capacity / initial capacity

BATTERY_CHARGE_EFF = 0.8      # fraction
BATTERY_DISCHARGE_EFF = 0.8   # fraction
# Space-qualified Li-ion pack: roughly 300-1000 EUR/Wh incl. qualification, BMS, housing.
# At ~200 Wh/kg that is ~60-200 k EUR/kg; commercial cells (~0.1 EUR/Wh) are not representative.
BATTERY_SPECIFIC_COST = 100e3  # EUR/kg, ROUGH estimate
BATTERY_CYCLE_DURABILITY = 1200 # 400 - 1200 cycles
BATTERY_RATED_DOD = 1.0       # fraction, DoD at which BATTERY_CYCLE_DURABILITY is rated
BATTERY_CYCLE_EXPONENT = 1.5  # k in N = N_rated * (DoD/DoD_rated)^-k; 1.5-2, lower = conservative


## WE NEED TO CALCULATE: MASS SIZE BATTERIES MASS SIZE SOLAR PANELS mass size RTG
RTG_DECAY_HALF_LIFE = 87.7 * C.YEAR  # s, Pu-238

# ---------- Shared: solar array performance ----------
# Size at Mercury aphelion: lowest solar flux -> worst case for array area
SOLAR_FLUX = C.SOLAR_FLUX_1AU * (C.AU / C.MERCURY_APHELION)**2  # [W/m²]
TEMP_FACTOR = 1 + POWER_TEMP_COEFF * (CELL_OPERATING_TEMP - CELL_REFERENCE_TEMP)

# EOL power produced per m² of panel
ARRAY_POWER_DENSITY = (
    SOLAR_FLUX * CELL_EFFICIENCY_REF * TEMP_FACTOR * ARRAY_PACKING_FACTOR
    * np.cos(SUN_INCIDENCE_ANGLE) * ARRAY_EOL_FACTOR
)  # [W/m²]

# ---------- Shared: load during eclipse ----------
# Duty-cycled instruments use their orbit-average power; laser is active in eclipse.
# Comms assumed on during eclipse (conservative, occultation may not coincide).
ECLIPSE_POWER = (
    HSRC_a * 0.2 + HSRC_i * 0.8 + UVS * 0.25 + MAG + Laser_a
    + OBDHpower + COMMpower_data + ADCSpower + TCpower
) * (1 + POWER_MARGIN)  # [W]
ECLIPSE_ENERGY = ECLIPSE_POWER * MAX_ECLIPSE_DURATION / C.WH_TO_J  # [Wh]

# ---------- Shared: energy used per orbit ----------
ORBIT_ENERGY = (

    (HSRC_a * 0.2 *ORBITAL_PERIOD + HSRC_i * 0.8 * ORBITAL_PERIOD + UVS *0.25 * ORBITAL_PERIOD + MAG * ORBITAL_PERIOD + Laser_a * MAX_ECLIPSE_DURATION + Laser_i * SUNLIGHT_DURATION) +
    PROPpower * 0 + OBDHpower * ORBITAL_PERIOD + COMMpower_data * DATA_TRANS_PERIOD + ADCSpower *ORBITAL_PERIOD + TCpower * ORBITAL_PERIOD +STRUCpower * 0
) * (1+POWER_MARGIN) # [j]

# ---------- Shared: battery discharge cycles ----------
# One discharge cycle per eclipsing orbit. For a polar orbit the Sun sweeps the beta
# angle through all values over a Mercury year, and an orbit is only eclipsed while
# |beta| < asin(R / r), i.e. for a fraction asin(R / r) / 90° of the orbits.
SCIENCE_ORBITS = int(C.SCIENCE_DURATION / ORBITAL_PERIOD)
BATTERY_CYCLES = SCIENCE_ORBITS

# Deepest discharge that still survives BATTERY_CYCLES, capped at the allowed max
BATTERY_CYCLE_DOD = BATTERY_RATED_DOD * (BATTERY_CYCLE_DURABILITY / BATTERY_CYCLES) ** (1 / BATTERY_CYCLE_EXPONENT)
BATTERY_DOD = min(BATTERY_MAX_DOD, BATTERY_CYCLE_DOD)

##CASE 1 (SOLAR):

ORBITAL_POWER = ORBIT_ENERGY / SUNLIGHT_DURATION # [W]

# Array must also cover distribution losses between array and loads
ARRAY_POWER_REQ = ORBITAL_POWER / (ARRAY_TO_BUS_EFF * BUS_TO_LOAD_EFF)  # [W]

SOLAR_ARRAY_SIZE = ARRAY_POWER_REQ / ARRAY_POWER_DENSITY  # [m²]
SOLAR_ARRAY_MASS = SOLAR_ARRAY_SIZE * ARRAY_AREAL_MASS    # [kg]

# ---------- Battery: supplies all loads during the longest eclipse ----------
# Energy that must be stored so the loads still get ECLIPSE_ENERGY at EOL
BATTERY_CAPACITY = ECLIPSE_ENERGY / (
    BATTERY_DOD * BATTERY_EOL_CAPACITY * BATTERY_DISCHARGE_EFF
    * BATTERY_TO_BUS_EFF * BUS_TO_LOAD_EFF
)  # [Wh]

BATTERY_MASS = BATTERY_CAPACITY / BATTERY_SPECIFIC_ENERGY  # [kg]
BATTERY_VOLUME = BATTERY_CAPACITY / BATTERY_ENERGY_DENSITY  # [L]

EPS_MASS = SOLAR_ARRAY_MASS + BATTERY_MASS + PMAD_MASS  # [kg]
EPS_MASS_MARGIN = EPS_MASS * (1 + MASS_MARGIN)          # [kg]

ARRAY_COST = SOLAR_ARRAY_SIZE * ARRAY_SPECIFIC_COST                          # [EUR]
BATTERY_COST = BATTERY_MASS * BATTERY_SPECIFIC_COST                           # [EUR]
PMAD_COST = PMAD_MASS * PMAD_SPECIFIC_COST                                   # [EUR]
EPS_COST = ARRAY_COST + BATTERY_COST + PMAD_COST                             # [EUR]

print("=" * 45)
print(" EPS SIZING - CASE 1 (SOLAR + BATTERY)")
print("=" * 45)
print("Power budget")
print(f"  Orbit energy           {ORBIT_ENERGY / C.WH_TO_J:10.1f} Wh")
print(f"  Required sunlit power  {ORBITAL_POWER:10.1f} W")
print(f"  Eclipse load           {ECLIPSE_POWER:10.1f} W")
print("Solar array")
print(f"  Solar flux (aphelion)  {SOLAR_FLUX:10.1f} W/m²")
print(f"  EOL power density      {ARRAY_POWER_DENSITY:10.1f} W/m²")
print(f"  Array power required   {ARRAY_POWER_REQ:10.1f} W")
print(f"  Array area             {SOLAR_ARRAY_SIZE:10.2f} m²")
print(f"  Array mass             {SOLAR_ARRAY_MASS:10.2f} kg")
print("Battery")
print(f"  Eclipse energy         {ECLIPSE_ENERGY:10.1f} Wh")
print(f"  Battery capacity       {BATTERY_CAPACITY:10.1f} Wh")
print(f"  Battery mass           {BATTERY_MASS:10.2f} kg")
print(f"  Battery volume         {BATTERY_VOLUME:10.2f} L")
print(f"  Discharge cycles       {BATTERY_CYCLES:10d}  of {SCIENCE_ORBITS} orbits")
print(f"  DoD for cycle life     {BATTERY_CYCLE_DOD * 100:10.1f} %  ({BATTERY_CYCLE_DURABILITY} cycles at {BATTERY_RATED_DOD * 100:.0f}%)")
print(f"  DoD used               {BATTERY_DOD * 100:10.1f} %  (max {BATTERY_MAX_DOD * 100:.0f}%)")
print("EPS mass")
print(f"  Solar array            {SOLAR_ARRAY_MASS:10.2f} kg")
print(f"  Battery                {BATTERY_MASS:10.2f} kg")
print(f"  PMAD                   {PMAD_MASS:10.2f} kg")
print(f"  Total                  {EPS_MASS:10.2f} kg")
print(f"  Total + {MASS_MARGIN * 100:.0f}% margin     {EPS_MASS_MARGIN:10.2f} kg")
print("EPS cost (rough)")
print(f"  Solar array            {ARRAY_COST / 1e6:10.2f} M EUR")
print(f"  Battery                {BATTERY_COST / 1e6:10.2f} M EUR")
print(f"  PMAD                   {PMAD_COST / 1e6:10.2f} M EUR")
print(f"  Total                  {EPS_COST / 1e6:10.2f} M EUR")
print("=" * 45)

CASE1_MASS, CASE1_MASS_MARGIN, CASE1_COST = EPS_MASS, EPS_MASS_MARGIN, EPS_COST

##CASE 2 (SOLAR + RTG):
# RTG powers the spacecraft on its own during hibernation (cruise), so the solar
# array isn't degrading before science starts. In science the RTG keeps running as
# a base load; solar array + a small battery cover the rest, same method as case 1.

HIBERNATION_LOAD = POWER_HIBERNATION * (1 + POWER_MARGIN)  # [W]

# RTG sized to still cover hibernation at the end of the transfer
transfer = TRANSFER_DURATION or 0  # s, None -> no decay during cruise counted
RTG_POWER_REQ = HIBERNATION_LOAD / BUS_TO_LOAD_EFF                        # [W]
RTG_POWER_BOL = RTG_POWER_REQ / 0.5 ** (transfer / RTG_DECAY_HALF_LIFE)   # [W]
RTG_POWER_EOL = RTG_POWER_BOL * 0.5 ** ((transfer + C.SCIENCE_DURATION) / RTG_DECAY_HALF_LIFE)  # [W]
RTG_MASS = RTG_POWER_BOL / RTG_SPEC_POWER  # [kg]
RTG_COST = RTG_POWER_BOL / RTG_SPEC_COST   # [EUR]

# Worst science-phase RTG contribution to the loads (end of science)
RTG_LOAD = RTG_POWER_EOL * BUS_TO_LOAD_EFF  # [W]

# Solar array: remaining orbit energy, delivered during sunlight only
SOLAR_ORBIT_ENERGY = ORBIT_ENERGY - RTG_LOAD * ORBITAL_PERIOD  # [J]
ORBITAL_POWER = SOLAR_ORBIT_ENERGY / SUNLIGHT_DURATION         # [W]
ARRAY_POWER_REQ = ORBITAL_POWER / (ARRAY_TO_BUS_EFF * BUS_TO_LOAD_EFF)  # [W]

SOLAR_ARRAY_SIZE = ARRAY_POWER_REQ / ARRAY_POWER_DENSITY  # [m²]
SOLAR_ARRAY_MASS = SOLAR_ARRAY_SIZE * ARRAY_AREAL_MASS    # [kg]

# Battery: eclipse load not covered by the RTG
BATTERY_ECLIPSE_POWER = ECLIPSE_POWER - RTG_LOAD                          # [W]
BATTERY_ECLIPSE_ENERGY = BATTERY_ECLIPSE_POWER * MAX_ECLIPSE_DURATION / C.WH_TO_J  # [Wh]
BATTERY_CAPACITY = BATTERY_ECLIPSE_ENERGY / (
    BATTERY_DOD * BATTERY_EOL_CAPACITY * BATTERY_DISCHARGE_EFF
    * BATTERY_TO_BUS_EFF * BUS_TO_LOAD_EFF
)  # [Wh]

BATTERY_MASS = BATTERY_CAPACITY / BATTERY_SPECIFIC_ENERGY  # [kg]
BATTERY_VOLUME = BATTERY_CAPACITY / BATTERY_ENERGY_DENSITY  # [L]

EPS_MASS = RTG_MASS + SOLAR_ARRAY_MASS + BATTERY_MASS + PMAD_MASS  # [kg]
EPS_MASS_MARGIN = EPS_MASS * (1 + MASS_MARGIN)                     # [kg]

ARRAY_COST = SOLAR_ARRAY_SIZE * ARRAY_SPECIFIC_COST                          # [EUR]
BATTERY_COST = BATTERY_MASS * BATTERY_SPECIFIC_COST                           # [EUR]
PMAD_COST = PMAD_MASS * PMAD_SPECIFIC_COST                                   # [EUR]
EPS_COST = RTG_COST + ARRAY_COST + BATTERY_COST + PMAD_COST                  # [EUR]

print("=" * 45)
print(" EPS SIZING - CASE 2 (SOLAR + RTG)")
print("=" * 45)
print("Power budget")
print(f"  Orbit energy           {ORBIT_ENERGY / C.WH_TO_J:10.1f} Wh")
print(f"  Hibernation load       {HIBERNATION_LOAD:10.1f} W")
print(f"  Eclipse load           {ECLIPSE_POWER:10.1f} W")
print("RTG")
if TRANSFER_DURATION is None:
    print("  (TRANSFER_DURATION not set: cruise decay ignored)")
print(f"  Power BOL              {RTG_POWER_BOL:10.1f} W")
print(f"  Power end of science   {RTG_POWER_EOL:10.1f} W")
print(f"  Load covered (science) {RTG_LOAD:10.1f} W")
print(f"  RTG mass               {RTG_MASS:10.1f} kg")
print(f"  RTG cost               {RTG_COST / 1e6:10.1f} M EUR")
print("Solar array")
print(f"  Solar flux (aphelion)  {SOLAR_FLUX:10.1f} W/m²")
print(f"  EOL power density      {ARRAY_POWER_DENSITY:10.1f} W/m²")
print(f"  Array power required   {ARRAY_POWER_REQ:10.1f} W")
print(f"  Array area             {SOLAR_ARRAY_SIZE:10.2f} m²")
print(f"  Array mass             {SOLAR_ARRAY_MASS:10.2f} kg")
print("Battery")
print(f"  Eclipse energy         {BATTERY_ECLIPSE_ENERGY:10.1f} Wh")
print(f"  Battery capacity       {BATTERY_CAPACITY:10.1f} Wh")
print(f"  Battery mass           {BATTERY_MASS:10.2f} kg")
print(f"  Battery volume         {BATTERY_VOLUME:10.2f} L")
print(f"  Discharge cycles       {BATTERY_CYCLES:10d}  of {SCIENCE_ORBITS} orbits")
print(f"  DoD for cycle life     {BATTERY_CYCLE_DOD * 100:10.1f} %  ({BATTERY_CYCLE_DURABILITY} cycles at {BATTERY_RATED_DOD * 100:.0f}%)")
print(f"  DoD used               {BATTERY_DOD * 100:10.1f} %  (max {BATTERY_MAX_DOD * 100:.0f}%)")
print("EPS mass")
print(f"  RTG                    {RTG_MASS:10.2f} kg")
print(f"  Solar array            {SOLAR_ARRAY_MASS:10.2f} kg")
print(f"  Battery                {BATTERY_MASS:10.2f} kg")
print(f"  PMAD                   {PMAD_MASS:10.2f} kg")
print(f"  Total                  {EPS_MASS:10.2f} kg")
print(f"  Total + {MASS_MARGIN * 100:.0f}% margin     {EPS_MASS_MARGIN:10.2f} kg")
print("EPS cost (rough)")
print(f"  RTG                    {RTG_COST / 1e6:10.2f} M EUR")
print(f"  Solar array            {ARRAY_COST / 1e6:10.2f} M EUR")
print(f"  Battery                {BATTERY_COST / 1e6:10.2f} M EUR")
print(f"  PMAD                   {PMAD_COST / 1e6:10.2f} M EUR")
print(f"  Total                  {EPS_COST / 1e6:10.2f} M EUR")
print("=" * 45)

# ---------- Comparison ----------
print()
print("=" * 45)
print(" EPS COMPARISON")
print("=" * 45)
print(f"  {'':22} {'Case 1':>9} {'Case 2':>9}")
print(f"  {'Mass [kg]':22} {CASE1_MASS:9.1f} {EPS_MASS:9.1f}")
print(f"  {'Mass + margin [kg]':22} {CASE1_MASS_MARGIN:9.1f} {EPS_MASS_MARGIN:9.1f}")
print(f"  {'Cost [M EUR]':22} {CASE1_COST / 1e6:9.2f} {EPS_COST / 1e6:9.2f}")
print("=" * 45)
