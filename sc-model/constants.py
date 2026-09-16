import numpy as np


# ---------- Physical constants ----------
AU = 149_597_870_700.0       # m
SOLAR_FLUX_1AU = 1361.0     # W/m², nominal solar irradiance at 1 AU
SIGMA_SB = 5.670374419e-8    # W/(m² K⁴), Stefan–Boltzmann constant
G0 = 9.80665                # m/s², standard gravity

HOUR = 3600.0               # s
DAY = 86400.0               # s
YEAR = 365.25 * DAY         # s
WH_TO_J = 3600.0            # J/Wh


# ---------- Mercury: approximate reference values ----------
MERCURY_RADIUS = 2.4397e6   # m
MERCURY_MU = 2.2032e13      # m³/s², gravitational parameter
MERCURY_PERIHELION = 0.3075 * AU  # m
MERCURY_APHELION = 0.4667 * AU    # m


# ---------- Mission inputs: confirm against your design ----------
ORBIT_ALTITUDE = 750e3      # m, nominal circular orbit
SCIENCE_DURATION = 1 * YEAR # s


# Fill these from your mission analysis / subsystem power budget.
