import numpy as np



"""
Mercury Orbiter - Preliminary Design (Rev 4) - dimensions from D2_2 drawing.
All values converted to SI [m] (drawing is in mm unless stated otherwise).
Angles in [deg].

Body frame (from isometric view):
    Z : along the cylinder axis, pointing to the top face (LV adapter side);
        main thruster is on the -Z face
    Y : towards the parabolic antenna side
    X : completes the right-handed triad
Origin assumed at the centre of the bottom face (main thruster side).

NOTE: masses are not given on the drawing (WEIGHT = XXX) - add them yourself.
Values marked "# CHECK" are my best reading of an ambiguous dimension.
"""

import math
import constants as C

mm = 1e-3  # mm -> m

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
REACTION_WHEEL_DIM = 218 * mm               # "218 x 4" in A-A               # CHECK
N_RCS_THRUSTERS    = 8
RCS_THRUSTER_RADIUS = 30 * mm               # "R30 x 8" in FRONT view        # CHECK

# ---------------------------------------------------------------------------
# Projected areas (useful for SRP / drag torques)
# ---------------------------------------------------------------------------
BODY_SIDE_AREA     = BODY_DIAMETER * BODY_HEIGHT       # projected, side-on
BODY_TOP_AREA      = math.pi * BODY_RADIUS**2          # projected, along Z

##------------------------------
# Mass
##-------------------------------

mbol = 2282 #kg, beginning of life, wet mass
meol = 707 # kg, eol wet mass

# ---------- Propulsion: bipropellant main engine (MON-3 / MMH) ----------
ISP = 317                  # s, 400 N class apogee engine                       # CHECK
ENGINE_THRUST = 400        # N                                                  # CHECK
OX_FUEL_RATIO = 1.65       # MON-3 / MMH mixture ratio, oxidiser in the upper tank

# ---------- Flight phases ----------
# dv: estimated delta-V of the phase [m/s]. Only the SHARE of each phase is used:
# the budget is scaled so the rocket equation runs from mbol exactly to meol, i.e.
#   m_end / m_start = (meol / mbol) ** (dv / dv_total)
# so ISP only matters for the implied total delta-V (printed as a sanity check).
# Replace dv with the mission-analysis budget once available.
# Environment: body = planet orbited (None = heliocentric cruise), sun_distance
# = closest Sun distance in the phase (worst case for radiation pressure).
# burn = main engine fires during the phase (thrust misalignment torque).
PHASES = [
    dict(name="Launch", dv=0.0, burn=False,             # launcher provides escape
         body="Earth", altitude=250e3, density=1.0e-10,  # parking orbit, solar max  # CHECK
         sun_distance=C.EARTH_PERIHELION),
    dict(name="Transfer", dv=1600.0, burn=True,          # DSMs + TCMs               # CHECK
         body=None, sun_distance=C.MERCURY_PERIHELION),
    dict(name="MOI", dv=1600.0, burn=True,               # v_inf ~2 km/s -> 750 km circular  # CHECK
         body="Mercury", altitude=C.ORBIT_ALTITUDE, sun_distance=C.MERCURY_PERIHELION),
    dict(name="Operations", dv=250.0, burn=True,         # orbit maintenance + wheel offloading  # CHECK
         body="Mercury", altitude=C.ORBIT_ALTITUDE, sun_distance=C.MERCURY_PERIHELION),
    dict(name="EOL", dv=50.0, burn=True,                 # disposal                  # CHECK
         body="Mercury", altitude=C.ORBIT_ALTITUDE, sun_distance=C.MERCURY_PERIHELION),
]

DV_TOTAL = sum(p["dv"] for p in PHASES)                 # [m/s] estimated
DV_IMPLIED = ISP * C.G0 * np.log(mbol / meol)           # [m/s] what mbol/meol allow

m = mbol
for p in PHASES:
    p["m_start"] = m
    m *= (meol / mbol) ** (p["dv"] / DV_TOTAL)
    p["m_end"] = m

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


def mass_properties(m):
    """Centre of mass [m] and inertia tensor about it [kg m²] at total mass m [kg].
    Propellant above meol is split over the tanks by the mixture ratio (point masses)."""
    prop = m - meol
    masses = np.array([BUS_MASS, SA_MASS, HGA_MASS, MAG_BOOM_MASS, MAG_SENSOR_MASS,
                       prop * OX_FUEL_RATIO / (1 + OX_FUEL_RATIO), prop / (1 + OX_FUEL_RATIO)])
    positions = np.array([BUS_POS, SA_POS, HGA_POS, MAG_BOOM_POS, MAG_SENSOR_POS,
                          OX_TANK_POS, FUEL_TANK_POS])
    cm = masses @ positions / masses.sum()
    inertia = BUS_INERTIA.copy()
    for mi, ri in zip(masses, positions - cm):  # parallel axis theorem
        inertia += mi * (ri @ ri * np.eye(3) - np.outer(ri, ri))
    return cm, inertia


#-----------------
# Calculate Torques
#-----------------
# Worst-case (SMAD) disturbance torques. Every torque is given as
#   [Tx, Ty, Tz, |T|] = largest |component| about each body axis, and largest magnitude,
# each maximised separately over attitude and over the mass change within the phase
# (so the per-axis worst cases can come from different attitudes). The totals add the
# maxima as if they all lined up, which is a conservative upper bound.

# ---------- Environment ----------
BODIES = {
    # dipole: magnetic moment M [T m³], field B = 2 M / r³ over the pole (worst case)
    # dipole_offset: Mercury's dipole sits 0.2 R_M north of the planet centre
    # ir_flux: planetary IR at the surface [W/m²] (Mercury: subsolar 700 K at perihelion)
    "Earth":   dict(mu=C.EARTH_MU, radius=C.EARTH_RADIUS, dipole=7.96e15, dipole_offset=0.0,
                    albedo=0.30, ir_flux=237.0),
    "Mercury": dict(mu=C.MERCURY_MU, radius=C.MERCURY_RADIUS,
                    dipole=195e-9 * C.MERCURY_RADIUS**3, dipole_offset=0.2 * C.MERCURY_RADIUS,
                    albedo=0.12, ir_flux=C.SIGMA_SB * 700**4),
}
B_IMF_1AU = 6e-9           # T, interplanetary field at 1 AU, scaled with 1/r² (conservative)

# ---------- Spacecraft properties ----------
SC_DIPOLE = 1.0            # A m², residual magnetic dipole (SMAD default)             # CHECK
Q_BUS = 0.6                # reflectance factor, MLI / white-coated bus                 # CHECK
Q_SA  = 0.3                # reflectance factor, solar cells                            # CHECK
Q_HGA = 0.6                # reflectance factor, white-painted dish                     # CHECK
CD = 2.2                   # drag coefficient, flat plate in free molecular flow
THRUST_MISALIGNMENT = np.radians(0.25)  # engine thrust-vector misalignment          # CHECK
THRUST_OFFSET = 1 * mm     # lateral offset of the engine from the Z axis               # CHECK
RADIATOR_TEMP = 300        # K                                                          # CHECK
RADIATOR_EMISSIVITY = 0.85
RADIATOR_DIR = np.array([0.0, -1.0, 0.0])   # centre of the radiator arc, away from HGA  # CHECK


def sphere_directions(n=5000):
    """Roughly uniform unit vectors over the sphere (Fibonacci lattice)."""
    k = np.arange(n) + 0.5
    z = 1 - 2 * k / n
    phi = np.pi * (1 + 5**0.5) * k
    rho = np.sqrt(1 - z**2)
    return np.column_stack((rho * np.cos(phi), rho * np.sin(phi), z))


DIRECTIONS = sphere_directions()  # towards the radiation source / along the flow / to nadir


def worst_case(torque):
    """[max |Tx|, max |Ty|, max |Tz|, max |T|] [Nm] from torque vectors of shape (N, 3) or (3,)."""
    torque = np.atleast_2d(torque)
    return np.append(np.abs(torque).max(axis=0), np.linalg.norm(torque, axis=1).max())


def surfaces(s):
    """(area seen from each direction s [m²], centre of pressure [m], reflectance) per surface.
    s has shape (N, 3). No shadowing between surfaces (conservative)."""
    sx, sy, sz = s.T
    return [
        (BODY_SIDE_AREA * np.sqrt(np.clip(1 - sz**2, 0, None)), BUS_POS, Q_BUS),
        (BODY_TOP_AREA * np.clip(sz, 0, None), np.array([0.0, 0.0, BODY_HEIGHT]), Q_BUS),
        (BODY_TOP_AREA * np.clip(-sz, 0, None), np.zeros(3), Q_BUS),
        (SA_PANEL_AREA * np.sqrt(np.clip(1 - (s @ SA_AXIS)**2, 0, None)), SA_POS, Q_SA),
        (HGA_AREA * np.abs(sy), HGA_POS, Q_HGA),
    ]


def pressure_torque(pressure, cm, aero=False):
    """Worst-case torque [Nm] from a uniform pressure [N/m²] arriving from any direction.
    Flat-plate model: F = p A (1 + q) for radiation, F = p A C_D for drag, along the flow."""
    torque = np.zeros_like(DIRECTIONS)
    for area, centre, q in surfaces(DIRECTIONS):
        coeff = CD if aero else 1 + q
        force = -pressure * coeff * area[:, None] * DIRECTIONS  # pushes away from the source
        torque += np.cross(centre - cm, force)
    return worst_case(torque)


#gravity gradient
def gravity_gradient_torque(mu, r, inertia):
    """T = 3 mu / r³ (o x I o), o = nadir in body frame, over all attitudes.
    Magnitude peaks at 3 mu / (2 r³) (I_max - I_min), 45 deg between principal axes."""
    o = DIRECTIONS
    return worst_case(3 * mu / r**3 * np.cross(o, o @ inertia))


#thermal
# Recoil of the radiator's own IR emission. Lambertian emitter: F = (2/3) M A_proj / c,
# with A_proj the chord-projected area of the radiator arc. The resultant acts through
# the cylinder axis at mid-height.
RADIATOR_PROJ_AREA = 2 * BODY_RADIUS * math.sin(math.radians(RADIATOR_ARC_ANGLE) / 2) * BODY_HEIGHT
RADIATOR_FORCE = (-(2 / 3) * RADIATOR_EMISSIVITY * C.SIGMA_SB * RADIATOR_TEMP**4
                  * RADIATOR_PROJ_AREA / C.SPEED_OF_LIGHT * RADIATOR_DIR)  # [N]


def thermal_torque(cm):
    """Body-fixed, so the components do not depend on attitude."""
    return worst_case(np.cross(BUS_POS - cm, RADIATOR_FORCE))


#magnetic
def magnetic_torque(field):
    """T = D x B. Neither the dipole direction nor B in body axes is known, so every
    axis can see the full D B."""
    return np.full(4, SC_DIPOLE * field)


#thrust misalignment (only while the main engine fires)
def thrust_torque(cm):
    """Engine on the -Z face, nominal thrust line along the Z axis.
    The CoM offset gives F (-cm_y, cm_x, 0); the engine offset and misalignment angle
    (direction unknown) add in the worst direction about X and Y. No torque about Z."""
    error = THRUST_OFFSET + cm[2] * math.tan(THRUST_MISALIGNMENT)  # [m]
    arm = np.hypot(cm[0], cm[1]) + error
    return ENGINE_THRUST * np.array([abs(cm[1]) + error, abs(cm[0]) + error, 0.0, arm])


def phase_torques(phase, m):
    """All disturbance torques [Nm] in a flight phase at spacecraft mass m [kg]."""
    cm, inertia = mass_properties(m)
    solar_flux = C.SOLAR_FLUX_1AU * (C.AU / phase["sun_distance"])**2  # [W/m²]
    body = BODIES.get(phase["body"])
    if body:
        r = body["radius"] + phase["altitude"]
        mu = body["mu"]
        view = (body["radius"] / r)**2                    # planet fills less of the sky with altitude
        planet_flux = (body["albedo"] * solar_flux + body["ir_flux"]) * view  # [W/m²]
        field = 2 * body["dipole"] / (r - body["dipole_offset"])**3           # [T]
    else:  # heliocentric cruise
        r = phase["sun_distance"]
        mu = C.SUN_MU
        planet_flux = 0.0
        field = B_IMF_1AU * (C.AU / r)**2
    dynamic_pressure = 0.5 * phase.get("density", 0.0) * mu / r  # [Pa], circular orbit speed

    #solar radiation torque, planetary albedo + IR, aerodynamic, magnetic
    return {
        "Gravity gradient": gravity_gradient_torque(mu, r, inertia),
        "Solar radiation":  pressure_torque(solar_flux / C.SPEED_OF_LIGHT, cm),
        "Planet albedo+IR": pressure_torque(planet_flux / C.SPEED_OF_LIGHT, cm),
        "Aerodynamic":      pressure_torque(dynamic_pressure, cm, aero=True),
        "Magnetic":         magnetic_torque(field),
        "Thermal":          thermal_torque(cm),
        "Thrust misalign.": thrust_torque(cm) if phase["burn"] else np.zeros(4),
    }


# Maximum of each torque over the phase (mass sampled from start to end)
for p in PHASES:
    samples = [phase_torques(p, mi) for mi in np.linspace(p["m_start"], p["m_end"], 5)]
    p["torques"] = {key: np.max([s[key] for s in samples], axis=0) for key in samples[0]}
    p["total_coast"] = sum(v for k, v in p["torques"].items() if k != "Thrust misalign.")
    p["total"] = sum(p["torques"].values())


# ---------- Output ----------
W = 20 + 12 * len(PHASES)
print("=" * W)
print(" MASS PER FLIGHT PHASE")
print("=" * W)
print(f"  {'':18}" + "".join(f"{p['name']:>12}" for p in PHASES))
print(f"  {'dV est. [m/s]':18}" + "".join(f"{p['dv']:12.0f}" for p in PHASES))
print(f"  {'Mass start [kg]':18}" + "".join(f"{p['m_start']:12.1f}" for p in PHASES))
print(f"  {'Mass end [kg]':18}" + "".join(f"{p['m_end']:12.1f}" for p in PHASES))
print(f"  {'Propellant [kg]':18}" + "".join(f"{p['m_start'] - p['m_end']:12.1f}" for p in PHASES))
cms = [mass_properties(p["m_start"])[0] for p in PHASES]
print(f"  {'CoM z [m]':18}" + "".join(f"{cm[2]:12.3f}" for cm in cms))
print(f"  {'CoM off-axis [mm]':18}" + "".join(f"{np.hypot(cm[0], cm[1]) / mm:12.1f}" for cm in cms))
for i, axis in enumerate("xyz"):
    print(f"  {f'I{axis}{axis} [kg m^2]':18}"
          + "".join(f"{mass_properties(p['m_start'])[1][i, i]:12.0f}" for p in PHASES))
print(f"  dV estimated {DV_TOTAL:.0f} m/s, implied by mbol/meol at Isp {ISP} s: {DV_IMPLIED:.0f} m/s"
      f" (x{DV_IMPLIED / DV_TOTAL:.2f})")
print("=" * W)

for p in PHASES:
    print()
    print("=" * 70)
    print(f" MAXIMUM DISTURBANCE TORQUES - {p['name'].upper()} [Nm]")
    print("=" * 70)
    print(f"  {'':18}" + "".join(f"{label:>12}" for label in ("Tx", "Ty", "Tz", "|T|")))
    for key, value in p["torques"].items():
        print(f"  {key:18}" + "".join(f"{v:12.2e}" for v in value))
    print("-" * 70)
    print(f"  {'Total, coasting':18}" + "".join(f"{v:12.2e}" for v in p["total_coast"]))
    print(f"  {'Total, burning':18}" + "".join(f"{v:12.2e}" for v in p["total"]))
    print("=" * 70)

print()
print("=" * W)
print(" MAXIMUM DISTURBANCE TORQUE MAGNITUDE PER FLIGHT PHASE [Nm]")
print("=" * W)
print(f"  {'':18}" + "".join(f"{p['name']:>12}" for p in PHASES))
for key in PHASES[0]["torques"]:
    print(f"  {key:18}" + "".join(f"{p['torques'][key][3]:12.2e}" for p in PHASES))
print("-" * W)
print(f"  {'Total, coasting':18}" + "".join(f"{p['total_coast'][3]:12.2e}" for p in PHASES))
print(f"  {'Total, burning':18}" + "".join(f"{p['total'][3]:12.2e}" for p in PHASES))
print("=" * W)