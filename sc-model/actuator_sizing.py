from spacecraft import meol, BUS_INERTIA, mass_properties, BODY_HEIGHT, mbol, BODY_DIAMETER, BUS_INERTIA
import numpy as np
import matplotlib.pyplot as plt
import math

############################################################
#reaction wheels
############################################################
T_periodical_correction =np.array([100*10**(-6) , 230*10**(-6), 230*10**(-6)])
T_max = np.array([0.0324732960, 0.0438448000, 0.0325321465]) #max disturbance torques
max_torque_SF = 1.5
T_max_with_SF = max_torque_SF * T_max

h = 1
a = 1
L = np.sqrt(h*h + 9*a*a/4)
d = np.sqrt(h*h + a*a)
SQRT3 = np.sqrt(3)

#unit vectors for the reaction wheel axes:
RW1_axis = np.array([h, 0, a]) / d
RW2_axis = np.array([-h/2, SQRT3*h/2, a]) / d
RW3_axis = np.array([-h/2, -SQRT3*h/2, a]) / d
RW4_axis = np.array([0, 0, -1])

wheel_axis_matrix = np.array([RW1_axis, RW2_axis, RW3_axis, RW4_axis]).transpose()

# Draw the RW axes
"""
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
origin = np.array([0, 0, 0])
ax.quiver(*origin, *RW1_axis, color='r', label='v1')
ax.quiver(*origin, *RW2_axis, color='g', label='v2')
ax.quiver(*origin, *RW3_axis, color='b', label='v3')
ax.quiver(*origin, *RW4_axis, color='r', label='v4')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.legend()
plt.show()
"""

#RW_radius = 0.1
#RW_height = 0.05
RW_material_density = 2700 #aluminum, kg/m3
#RW_mass = RW_material_density * math.pi * RW_radius*RW_radius * RW_height

def RPM_to_radPerSec(rpm):
    return rpm*2*math.pi/60

T_momentum_dumping = 15*60
orbital_P = 127 * 60
T_until_momentum_dumping = orbital_P - T_momentum_dumping #once per orbit

#RW_MMOI = 0.5 * RW_mass * RW_radius * RW_radius #1/2 mr^2

#RW_motor_torque = 0.2 #N/m
#RW_max_angular_accel = RW_motor_torque / RW_MMOI
RW_max_angular_momentum = max(T_max_with_SF) * T_until_momentum_dumping
RW_max_angular_vel = RPM_to_radPerSec(6000)
RW_MMOI = RW_max_angular_momentum / RW_max_angular_vel
ratio_h_to_r = 1/5
radius_RW = math.pow(2*RW_MMOI/ (RW_material_density * math.pi * ratio_h_to_r) , 1/5)
height_RW = ratio_h_to_r * radius_RW
mass = radius_RW ** 2 * math.pi * height_RW * RW_material_density

print(f"height is {height_RW} and radius is {radius_RW} MMOI is {RW_MMOI} mass is {mass}")

I_w = np.array([RW_MMOI, RW_MMOI, RW_MMOI, RW_MMOI]) #array with mmoi for each rw. all the same but this array allows for them to be different

def RW_angular_accels_To_SC_torque(RW_angular_accelerations):#ang accels: rad/s/s for each RW (there are 4 RW's)
    T_sc = -wheel_axis_matrix @ (RW_MMOI * RW_angular_accelerations)
    return T_sc

def compute_RW_angular_accels_for_desired_torques(T_desired):
    B = wheel_axis_matrix @ np.diag(I_w)
    alpha = -np.linalg.pinv(B) @ T_desired
    return alpha




############################################################
#thrusters for momentum dumping
#############################################################

h_max_vector = RW_max_angular_momentum*(RW1_axis + RW2_axis + RW3_axis + RW4_axis)
#print(h_max_vector)
dumping_time = 0.1 #s
moment_arm_x = BODY_DIAMETER * 0.5
moment_arm_y = moment_arm_x
moment_arm_z = BODY_HEIGHT * 0.5

thrust_dumping = np.array((
    h_max_vector[0] / (moment_arm_y * dumping_time) * 0.5, 
    h_max_vector[1] / (moment_arm_z * dumping_time) * 0.5, 
    h_max_vector[2] / (moment_arm_x * dumping_time) * 0.5
))

dt = 0.1
RW_decel = RW_max_angular_vel / dt
torques = RW_angular_accels_To_SC_torque(np.array([RW_decel, RW_decel, RW_decel, RW_decel]))
thrusts = np.array([
    torques[0]/moment_arm_x,
    torques[1]/moment_arm_y,
    torques[2]/moment_arm_z
])
#print("thrusts", thrusts)

#print("Thrust needed per axis for momentum dumping is:", thrust_dumping)





############################################################
#cg considerations and change effects
#############################################################

#getting the cg and inertia, originall version
cg_original, inertia_original = mass_properties(mbol)
cg_original_endoflife, inertia_original = mass_properties(meol)



#parameters to then change the MMOI w change in actuator size, code taken from spacecraft.py on 12/10


"""
Mercury Orbiter - spacecraft size and mass. Preliminary Design (Rev 4), D2_2 drawing.
All values converted to SI [m] (drawing is in mm unless stated otherwise).
Angles in [deg]. Values marked "# CHECK" are a best reading of an ambiguous dimension.

Body frame (from isometric view):
    Z : along the cylinder axis, pointing to the top face (LV adapter side);
        main thruster is on the -Z face
    Y : towards the parabolic antenna side
    X : completes the right-handed triad
Origin assumed at the centre of the bottom face (main thruster side).
"""

import math
import numpy as np

mm = 1e-3  # mm -> m

# =====================================================================
# SIZE
# =====================================================================

# ---------------------------------------------------------------------------
# Main bus (cylinder)
# ---------------------------------------------------------------------------
BODY_HEIGHT        = 3510 * mm        # LEFT view, bottom face to top face
BODY_DIAMETER      = 2025 * mm        # LEFT view width
BODY_RADIUS        = BODY_DIAMETER / 2
SHELL_LVL1_HEIGHT  = 2900 * mm        # A-A, bottom face to shell level 1 (tank bay)

# ---------------------------------------------------------------------------
# Launch-vehicle adapter (top face)
# ---------------------------------------------------------------------------
LV_ADAPTER_RADIUS  = 468.5 * mm       # TOP view

# ---------------------------------------------------------------------------
# Propellant tanks (spherical, stacked along Z, section A-A)
# ---------------------------------------------------------------------------
OX_TANK_RADIUS     = 690 * mm         # upper tank
FUEL_TANK_RADIUS   = 721 * mm         # lower tank

# ---------------------------------------------------------------------------
# Solar array (single wing, TOP view)
# ---------------------------------------------------------------------------
SA_PANEL_LENGTH    = 2012 * mm        # along the wing
SA_PANEL_WIDTH     = 1006 * mm
SA_PANEL_AREA      = SA_PANEL_LENGTH * SA_PANEL_WIDTH
SA_SPAN_FROM_BODY  = 2332 * mm        # body outer surface -> panel tip
SA_GAP_FROM_BODY   = SA_SPAN_FROM_BODY - SA_PANEL_LENGTH          # yoke length (0.320 m)
SA_CENTRE_ARM      = BODY_RADIUS + SA_GAP_FROM_BODY + SA_PANEL_LENGTH / 2  # from body axis

# ---------------------------------------------------------------------------
# Magnetometer boom (TOP view)
# ---------------------------------------------------------------------------
MAG_BOOM_LENGTH    = 3800 * mm

# ---------------------------------------------------------------------------
# Parabolic high-gain antenna (LEFT / FRONT view)
# ---------------------------------------------------------------------------
HGA_DIAMETER       = 1.48             # given in [m] on the drawing
HGA_RADIUS         = HGA_DIAMETER / 2
HGA_AREA           = math.pi * HGA_RADIUS**2
HGA_DEPTH          = 265.22 * mm      # FRONT view, dish depth / standoff   # CHECK

# ---------------------------------------------------------------------------
# Radiator (TOP view)
# ---------------------------------------------------------------------------
RADIATOR_ARC_ANGLE = 106              # [deg] arc of the body covered
RADIATOR_AREA      = math.radians(RADIATOR_ARC_ANGLE) * BODY_RADIUS * BODY_HEIGHT  # if full height  # CHECK

# ---------------------------------------------------------------------------
# Payload boxes (TOP view)
# ---------------------------------------------------------------------------
UNLABELED_BOX_SIZE = (250 * mm, 250 * mm)   # square box next to LV adapter  # CHECK
UNLABELED_BOX_OFFSET = 382 * mm             # dimension below that box       # CHECK
HR_CAMERA_WIDTH    = 300 * mm
HR_CAMERA_DIM2     = 515 * mm               # vertical dim next to camera    # CHECK
SPECTROGRAPH_DIM   = 346 * mm               # vertical dim next to box       # CHECK

# ---------------------------------------------------------------------------
# Avionics boxes (section B-B)  (width, height)
# ---------------------------------------------------------------------------
IMU_SIZE           = (350 * mm, 250 * mm)
OBC_SIZE           = (330 * mm, 270 * mm)
PCDU_SIZE          = (350 * mm, 210 * mm)

# ---------------------------------------------------------------------------
# ADCS / propulsion hardware
# ---------------------------------------------------------------------------
N_REACTION_WHEELS  = 4
REACTION_WHEEL_DIM = 242 * mm               # "218 x 4" in A-A               # CHECK
N_RCS_THRUSTERS    = 8
RCS_THRUSTER_RADIUS = 30 * mm               # "R30 x 8" in FRONT view        # CHECK

#part 2
RW_POS = np.array([0, BODY_RADIUS, 0.727*2])
RW_MASS = 24.0 * 4

# ---------------------------------------------------------------------------
# Projected areas (useful for SRP / drag torques)
# ---------------------------------------------------------------------------
BODY_SIDE_AREA     = BODY_DIAMETER * BODY_HEIGHT       # projected, side-on
BODY_TOP_AREA      = math.pi * BODY_RADIUS**2          # projected, along Z



# ---------- Propulsion: bipropellant main engine (MON-3 / MMH) ----------
ISP = 317                  # s, 400 N class apogee engine                       # CHECK
ENGINE_THRUST = 400        # N                                                  # CHECK
OX_FUEL_RATIO = 1.65       # MON-3 / MMH mixture ratio, oxidiser in the upper tank

# ---------- Mass distribution ----------
# Appendages and propellant as point masses; the rest of meol (dry mass + residual
# propellant) is a uniform solid cylinder filling the bus.
SA_MASS         = 15.0     # kg, panel + yoke + drive mechanism                  # CHECK
HGA_MASS        = 10.0     # kg, dish + feed + pointing mechanism                # CHECK
MAG_BOOM_MASS   = 3.0      # kg, boom structure, lumped at mid-boom              # CHECK
MAG_SENSOR_MASS = 1.0      # kg, magnetometer at the boom tip                    # CHECK
BUS_MASS = meol - SA_MASS - HGA_MASS - MAG_BOOM_MASS - MAG_SENSOR_MASS

# Appendage placement is not dimensioned on the drawing:
# solar wing along +X, magnetometer boom along -X, HGA on +Y, all at mid-height.  # CHECK
BUS_POS        = np.array([0.0, 0.0, BODY_HEIGHT / 2])
SA_POS         = np.array([SA_CENTRE_ARM, 0.0, BODY_HEIGHT / 2])
SA_AXIS        = np.array([1.0, 0.0, 0.0])  # wing axis; the panel rotates about it to track the Sun
HGA_POS        = np.array([0.0, BODY_RADIUS + HGA_DEPTH, BODY_HEIGHT / 2])
MAG_BOOM_POS   = np.array([-(BODY_RADIUS + MAG_BOOM_LENGTH / 2), 0.0, BODY_HEIGHT / 2])
MAG_SENSOR_POS = np.array([-(BODY_RADIUS + MAG_BOOM_LENGTH), 0.0, BODY_HEIGHT / 2])

# Spherical tanks stacked in the tank bay (below shell level 1), fuel at the bottom
TANK_GAP = (SHELL_LVL1_HEIGHT - 2 * FUEL_TANK_RADIUS - 2 * OX_TANK_RADIUS) / 2
FUEL_TANK_POS = np.array([0.0, 0.0, TANK_GAP + FUEL_TANK_RADIUS])
OX_TANK_POS   = FUEL_TANK_POS + np.array([0.0, 0.0, FUEL_TANK_RADIUS + OX_TANK_RADIUS])

# Solid cylinder about its own centre
BUS_INERTIA = BUS_MASS * np.diag([
    (3 * BODY_RADIUS**2 + BODY_HEIGHT**2) / 12,
    (3 * BODY_RADIUS**2 + BODY_HEIGHT**2) / 12,
    BODY_RADIUS**2 / 2,
])


def mass_properties2(m):
    """Centre of mass [m] and inertia tensor about it [kg m²] at total mass m [kg].
    Propellant above meol is split over the tanks by the mixture ratio (point masses)."""
    prop = m - meol
    masses = np.array([BUS_MASS, SA_MASS, HGA_MASS, MAG_BOOM_MASS, MAG_SENSOR_MASS,
                       prop * OX_FUEL_RATIO / (1 + OX_FUEL_RATIO), prop / (1 + OX_FUEL_RATIO), RW_MASS])
    positions = np.array([BUS_POS, SA_POS, HGA_POS, MAG_BOOM_POS, MAG_SENSOR_POS,
                          OX_TANK_POS, FUEL_TANK_POS, RW_POS])
    cm = masses @ positions / masses.sum()
    inertia = BUS_INERTIA.copy()
    for mi, ri in zip(masses, positions - cm):  # parallel axis theorem
        inertia += mi * (ri @ ri * np.eye(3) - np.outer(ri, ri))

    return [cm, inertia]

#cg_adapted, interia2 = mass_properties(mbol)

cm_adaptes_mbol, interia2 = mass_properties2(mbol)
cm_adaptes_meol, interia3 = mass_properties2(meol)

print(f"cg beginning of life {cm_adaptes_mbol}")
print(f"cg end of life {cm_adaptes_meol}")
print(f"cg WP2 {cg_original}")
print(f"cg WP2 at end of life{cg_original_endoflife}")
