# Physical constants and planetary data
import math

# Physical constants
BOLTZMANN_CONSTANT_DB = -228.6  # dB (J/K)
SPEED_OF_LIGHT = 3e8  # m/s
EARTH_RADIUS_KM = 6371  # km
AU = 1.495978707e11  # m 
K = 1.38e-23  # J/K
SYSTEM_NOISE_TEMP = 135 #K
G = 6.67408e-11


# Planetary distances from Sun (in meters)
PLANETS = {
    "Mercury": 1.39 * AU,
    "Venus": 1.72 * AU,
    "Earth": 1.0 * AU,
    "Mars": 2.52 * AU,
    "Jupiter": 6.20 * AU,
    "Saturn": 10.58 * AU,
    "Uranus": 20.22 * AU,
    "Neptune": 31.05 * AU,
    "Pluto": 40.48 * AU,
    "Moon": 0.00257 * AU
}

# Planetary weights (in kg)
PLANET_WEIGHTS = {
    "Mercury": 3.3022e23,
    "Venus": 4.8695e24,
    "Earth": 5.9723e24,
    "Mars": 6.4185e23,
    "Jupiter": 1.8986e27,
    "Saturn": 5.6844e26,
    "Uranus": 8.6810e25,
    "Neptune": 1.0243e26,
    "Pluto": 1.309e22,
    "Moon": 7.349e22
}
# Planetary radii (in meters)
PLANET_RADII = {
    "Mercury": 2439.4e3,
    "Venus": 6051.8e3,
    "Earth": 6371e3,
    "Mars": 3389.5e3,
    "Jupiter": 71492e3,
    "Saturn": 58232e3,
    "Uranus": 25362e3,
    "Neptune": 24622e3,
    "Pluto": 1188.3e3,
    "Moon": 1737.1e3
}
# Frequency bands (GHz)

# Default antenna efficiency
DEFAULT_ANTENNA_EFFICIENCY = 0.55

