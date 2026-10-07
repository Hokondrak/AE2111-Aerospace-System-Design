import numpy as np


# ---------- Physical constants ----------
AU = 149_597_870_700.0       # m
SOLAR_FLUX_1AU = 1361.0     # W/m², nominal solar irradiance at 1 AU
SIGMA_SB = 5.670374419e-8    # W/(m² K⁴), Stefan–Boltzmann constant
G0 = 9.80665                # m/s², standard gravity
SPEED_OF_LIGHT = 299_792_458.0  # m/s
BOLTZMANN = 1.380649e-23    # J/K

HOUR = 3600.0               # s
DAY = 86400.0               # s
YEAR = 365.25 * DAY         # s
WH_TO_J = 3600.0            # J/Wh


# ---------- Mercury: approximate reference values ----------
MERCURY_RADIUS = 2.4397e6   # m
MERCURY_MU = 2.2032e13      # m³/s², gravitational parameter
MERCURY_PERIHELION = 0.3075 * AU  # m
MERCURY_APHELION = 0.4667 * AU    # m
MERCURY_SYNODIC_PERIOD = 115.88 * DAY  # s, as seen from Earth

EARTH_PERIHELION = 0.9833 * AU    # m
EARTH_APHELION = 1.0167 * AU      # m
EARTH_RADIUS = 6.3781e6           # m
EARTH_MU = 3.986004418e14         # m³/s²

SUN_MU = 1.32712440018e20         # m³/s²


# ---------- Mission inputs: confirm against your design ----------
ORBIT_ALTITUDE = 750e3      # m, nominal circular orbit
SCIENCE_DURATION = 1 * YEAR # s
TRANSFER_DURATION = 6.7 * YEAR  # s

ORBITAL_PERIOD = 7630           # s
MAX_ECLIPSE_DURATION = 2115.2   # s
EARTH_OCCULTATION = 2118        # s, Earth hidden behind Mercury per orbit
