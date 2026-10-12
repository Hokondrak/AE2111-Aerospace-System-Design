# mass_properties.py
import math
import numpy as np

def compute_mass_properties(m, meol, bus_mass, bus_inertia, bus_pos, sa_pos, hga_pos, mag_boom_pos, mag_sensor_pos, ox_tank_pos, fuel_tank_pos, ox_fuel_ratio):
    """Centre of mass [m] and inertia tensor about it [kg m²] at total mass m [kg].
    Propellant above meol is split over the tanks by the mixture ratio (point masses)."""
    prop = m - meol
    masses = np.array([bus_mass, 15.0, 10.0, 3.0, 1.0,
                       prop * ox_fuel_ratio / (1 + ox_fuel_ratio), prop / (1 + ox_fuel_ratio)])
    positions = np.array([bus_pos, sa_pos, hga_pos, mag_boom_pos, mag_sensor_pos,
                          ox_tank_pos, fuel_tank_pos])
    cm = masses @ positions / masses.sum()
    inertia = bus_inertia.copy()
    for mi, ri in zip(masses, positions - cm):  # parallel axis theorem
        inertia += mi * (ri @ ri * np.eye(3) - np.outer(ri, ri))
    return cm, inertia

