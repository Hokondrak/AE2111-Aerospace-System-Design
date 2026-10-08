##Imports

import numpy as np
import scipy.integrate as sp
import spacecraft as sc
import torques as tq  
import constants as C
from scipy.spatial.transform import Rotation as Rot

######Functions

#two effects that change where the s/c points:
#the orbit around the planet itself (how to model this?)
#the disturbances,
#which turn on and off at every time
#so the flow would be:
#for each position in orbit: 
# 1. Determin orbit position from the circular orbit equation (deterministic)
# 2. Current angles [pitch, roll, yaw]
# 3. Calulate Torques from each of the sources
# 4. From that, integrate into angular acceleration
# 5. Integrate into angular velocity
# 6. Angular Position
# 7. Timestep
# Current angle, position -> Current Torques -> Current alpha -> current omega -> new position
#use euler first, then do rk6.

#plot


# 3. Torques from each of the sources, all as [Tx, Ty, Tz] [Nm] in body axes.
# Every direction is a unit vector in BODY axes, 
def disturbance_torques(m, sun_dir, nadir_dir, B_body,
                        mu, r, solar_pressure, planet_pressure):
    cm, inertia = sc.mass_properties(m)                                  # CoM [m], inertia [kg m²]
    return {
        "Gravity gradient": tq.gravity_gradient_torque(mu, r, inertia, nadir_dir),    #indep of orbital position
        "Solar radiation":  tq.pressure_torque(solar_pressure, sun_dir, cm),          #dependent on orbital position p = flux / c
        "Planet albedo+IR": tq.pressure_torque(planet_pressure, nadir_dir, cm),       #dependent? I Think comes from the planet
        "Magnetic":         tq.magnetic_torque(B_body),                    # # in [T], default s/c dipole
        "Thermal":          tq.thermal_torque(cm),                         #indep of orbital position
    }

# total torque: sum(disturbance_torques(...).values())

######
r  = C.MERCURY_RADIUS + C.ORBIT_ALTITUDE
sun_space = np.array([0.0, 0.0, 1.0])
mercury_space = np.array([0,0,1])
B0 = tq.BODIES["Mercury"]["dipole"] / r**3                          
mercury = tq.BODIES["Mercury"]
solar_flux = C.SOLAR_FLUX_1AU * (C.AU / C.MERCURY_PERIHELION)**2   # [W/m²] at Mercury perihelion
shadow_limit = -np.sqrt(1 - (C.MERCURY_RADIUS / r)**2)
m = tq.PHASES[3]["m_start"]   # Operations phase mass [kg]
cm, inertia = sc.mass_properties(m)

#Initiate empty arrays for plotting

n_log = []          # orbital position n [rad]
t_log = []          # time [s]
torque_log = []     # disturbance_torques(...) dict: [Tx, Ty, Tz] [Nm] per source
T_log = []          # total torque [Tx, Ty, Tz] [Nm]
error_log = []      # attitude error vs nadir pointing [pitch, roll, yaw] [rad]
attitude_log = []   # attitude vs the stars [phi, beta, gamma] [rad]
rate_log = []       # body rates dattitude [rad/s]
eclipse_log = []    # True while in Mercury's shadow
day_log = []        # how lit the ground below is, 0 (night) to 1 (noon)



#to begin:
n = 0 #start at equator, 0 at equator, 90 at north pole, 180 to the right of the planet, at equator, 270 at south
dn = np.sqrt(C.MERCURY_MU / r**3)   # rad/s angular speed around the orbit

phi = 0 #pitch
gamma = 0 #yaw
beta = 0 #roll

dphi = dn #to follow orbit
dgamma = 0
dbeta = 0

ddphi = 0
ddgamma = 0
ddbeta = 0

dt = 1

t = 0

# body axes [X, Y, Z] = [pitch, roll, yaw], same order as the torques [Tx, Ty, Tz]
attitude = Rot.identity()
dattitude = np.array([dphi, dbeta, dgamma])
ddattitude = np.array([ddphi, ddbeta, ddgamma])


#also precomputed from geometry, for simplicity reasons:
#sun is active between angles (sun is to the right, s/c starts on the left.), we assume 2D ish sim for what its worth


while n < 3 * 2* np.pi: # we do 3 orbits here to illustrate. I will do simple FE and then we'll see.
    
    #Determin orbit position from the circular orbit equation
    n = dn * t
    #we are turning around mercury so:
    mercury_space = np.array([0.0, -np.sin(n), np.cos(n)]) # where do we need to point in space coordinates to point to mercury
    B_space = B0 * np.array([0.0, 1 - 3 * np.sin(n)**2, 3 * np.sin(n) * np.cos(n)]) # where does the magnetic field point, from satellites POV.
    day = max(0.0, -mercury_space @ sun_space)   # 1 above the subsolar point, 0 over the night side
    planet_flux = (mercury["albedo"] * solar_flux + mercury["ir_flux"]) * day * (C.MERCURY_RADIUS / r)**2
    planet_pressure = planet_flux / C.SPEED_OF_LIGHT

    #whats going on around us?

    sun_body = attitude.inv().apply(sun_space)    #vector from s/c to sun, in s/c coordinates
    mercury_body = attitude.inv().apply(mercury_space)
    B_body = attitude.inv().apply(B_space)

    #shadow check
    if -mercury_space @ sun_space < shadow_limit:
        eclipse = True
    else:
        eclipse = False
    #Calulate Torques
    torques = disturbance_torques(
        m,
        sun_dir=sun_body,
        nadir_dir=mercury_body,
        B_body=B_body,
        mu=C.MERCURY_MU,
        r=r,
        solar_pressure=0.0 if eclipse else solar_flux / C.SPEED_OF_LIGHT,
        planet_pressure=planet_pressure,
    )
    T = sum(torques.values())

    #save each into a list (before integrating, so everything belongs to the same moment)
    reference = Rot.from_rotvec([n, 0, 0])                 # perfect nadir pointing at this n
    n_log.append(n)
    t_log.append(t)
    torque_log.append(torques)
    T_log.append(T)
    error_log.append((reference.inv() * attitude).as_rotvec())
    attitude_log.append(attitude.as_euler("XYZ"))
    rate_log.append(dattitude)
    eclipse_log.append(eclipse)
    day_log.append(day)

    #Compute angular acceleration
    ddattitude = np.linalg.solve(inertia, T - np.cross(dattitude, inertia @ dattitude))

    #Integrate into angular velocity
    dattitude = dattitude + ddattitude * dt

    #Integrate into Angular Position
    attitude = attitude * Rot.from_rotvec(dattitude * dt)


    #Timestep
    t = t + dt


# logs -> arrays for plotting, one row per timestep
n_log, t_log, T_log, error_log, attitude_log, rate_log, eclipse_log, day_log = map(
    np.array, (n_log, t_log, T_log, error_log, attitude_log, rate_log, eclipse_log, day_log))
torque_arrays = {name: np.array([d[name] for d in torque_log]) for name in torque_log[0]}  # (steps, 3) per source
    