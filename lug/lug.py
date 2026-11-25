import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

###Inputs
#Force
f_y = 4.53 * 2 * 9.81 * 0.5
f_z = 4.52 * 6 * 9.81 * 0.5
m_x = 117.85     # [N m] moment about x (normal to the lug plate), per lug 
Ftu = f_z
Fbry = f_y
Fu = f_y

#Geometry
y = None
l_over_d = 3     # lug base to hole centre: l = 3 * d
w = None
d = None
t = None

#material
sigma_y = 500e6 #Pa
rho = 2810    # [kg/m^3] aluminium (7075-T6); only scales the mass, doesn't change the optimum

#safety
SF = 1.5      # safety factor -- placeholder, set to your project's value
FF = 1.15     # fitting factor (chart notes: additional M.S. of 0.15 for fittings)

#limits (fit / manufacturing) -- placeholders, set to your design's values
d_bolt_min = 3.2e-3   # [m] smallest hole: clearance hole for an M3 bolt
gap_min    = 2e-3     # [m] smallest distance from the hole edge to the lug base (washer / nut / mating part)
t_manuf    = 2e-3     # [m] thinnest plate that can be manufactured

#MoI
I_p = None
I = None

#Geometry Coeffs.
k_e = None
# Kt vs W/D chart, curve 2, approximated by linear splines
KT_W_D = np.array([1.0, 2.5, 5.0])
KT_VAL = np.array([1.00, 0.91, 0.74])

def kt_func(w_d):
    """Kt from W/D; clamped to the chart's end values outside 1 <= W/D <= 5."""
    return np.interp(w_d, KT_W_D, KT_VAL)

# Kbru vs e/D chart, one linear spline per D/t curve: D/t -> (e/D points, Kbru points)
KBRU_CURVES = {
    2:  (np.array([0.5, 1.0, 1.5, 2.0, 3.45]),      np.array([0.0, 0.86, 1.50, 1.95, 2.80])),
    3:  (np.array([0.5, 1.0, 1.5, 2.0, 2.6, 4.0]),  np.array([0.0, 0.86, 1.50, 1.95, 2.27, 2.75])),
    4:  (np.array([0.5, 1.0, 1.5, 2.0, 2.6, 4.0]),  np.array([0.0, 0.86, 1.50, 1.92, 2.17, 2.52])),
    5:  (np.array([0.5, 1.0, 1.5, 2.0, 2.6, 4.0]),  np.array([0.0, 0.86, 1.47, 1.86, 2.06, 2.30])),
    6:  (np.array([0.5, 1.0, 1.4, 2.0, 2.8, 4.0]),  np.array([0.0, 0.86, 1.33, 1.78, 1.98, 2.07])),
    7:  (np.array([0.5, 1.0, 1.4, 2.4]),            np.array([0.0, 0.86, 1.25, 1.68])),
    8:  (np.array([0.5, 1.0, 1.4, 2.4]),            np.array([0.0, 0.86, 1.20, 1.52])),
    9:  (np.array([0.5, 1.05, 1.4, 2.4]),           np.array([0.0, 0.88, 1.13, 1.40])),
    10: (np.array([0.5, 1.05, 1.4, 2.4]),           np.array([0.0, 0.86, 1.07, 1.26])),
    15: (np.array([0.5, 1.0, 1.5, 2.4]),            np.array([0.0, 0.60, 0.77, 0.84])),
    20: (np.array([0.5, 1.0, 1.6, 2.4]),            np.array([0.0, 0.45, 0.58, 0.63])),
    25: (np.array([0.5, 1.0, 1.6, 2.4]),            np.array([0.0, 0.37, 0.47, 0.50])),
    30: (np.array([0.5, 1.0, 1.6, 2.4]),            np.array([0.0, 0.30, 0.38, 0.41])),
}


def interp_family(x, p, curves):
    """Read a chart that has one curve per value of p (e.g. one curve per D/t).
    Find the two curves that p lies between, read both at x, and blend linearly.
    Outside the chart, the nearest edge value is used."""
    ps = sorted(curves)
    p = np.clip(p, ps[0], ps[-1])
    k = 0
    for p_lo, p_hi in zip(ps[:-1], ps[1:]):
        k_lo = np.interp(x, *curves[p_lo])          # read the lower curve at x
        k_hi = np.interp(x, *curves[p_hi])          # read the upper curve at x
        frac = (p - p_lo) / (p_hi - p_lo)           # 0 on the lower curve, 1 on the upper
        between = (p >= p_lo) & (p <= p_hi)
        k = np.where(between, k_lo + frac * (k_hi - k_lo), k)
    return k

def kbru_func(e_d, d_t, t):
    """Kbru from e/D and D/t (chart range e/D 0.5-4, D/t 2-30)."""
    k = interp_family(e_d, d_t, KBRU_CURVES)
    return np.where(t >= 12.7e-3, np.minimum(k, 2.0), k)


# Kbry vs e/D chart (Fig D1.14, all materials), one linear spline per t/D curve
KBRY_CURVES = {
    0.06: (np.array([0.5, 0.73, 1.0, 1.5, 2.2, 4.0]), np.array([0.0, 0.48, 0.68, 0.88, 0.96, 1.00])),
    0.08: (np.array([0.5, 0.75, 1.0, 1.5, 2.2, 4.0]), np.array([0.0, 0.50, 0.77, 0.98, 1.09, 1.14])),
    0.10: (np.array([0.5, 0.75, 1.0, 1.5, 2.2, 4.0]), np.array([0.0, 0.50, 0.82, 1.06, 1.20, 1.25])),
    0.12: (np.array([0.5, 0.75, 1.0, 1.5, 2.2, 4.0]), np.array([0.0, 0.50, 0.84, 1.12, 1.27, 1.33])),
    0.15: (np.array([0.5, 0.75, 1.0, 1.5, 2.2, 4.0]), np.array([0.0, 0.50, 0.86, 1.20, 1.35, 1.42])),
    0.20: (np.array([0.5, 0.75, 1.0, 1.5, 2.0, 2.8, 4.0]), np.array([0.0, 0.50, 0.88, 1.28, 1.42, 1.49, 1.52])),
    0.30: (np.array([0.5, 0.75, 1.0, 1.5, 2.0, 2.8, 4.0]), np.array([0.0, 0.50, 0.90, 1.38, 1.52, 1.61, 1.64])),
    0.40: (np.array([0.5, 0.75, 1.0, 1.5, 2.0, 2.8, 4.0]), np.array([0.0, 0.50, 0.90, 1.42, 1.58, 1.67, 1.71])),
    0.60: (np.array([0.5, 0.75, 1.0, 1.5, 2.0, 2.5, 4.0]), np.array([0.0, 0.50, 0.90, 1.43, 1.60, 1.69, 1.76])),
}

def kbry_func(e_d, t_d):
    """Kbry from e/D and t/D (chart range e/D 0.5-4, t/D 0.06-0.6+)."""
    return interp_family(e_d, t_d, KBRY_CURVES)


# Ktu vs Aav/Abr chart (Fig D1.15), curve 11, approximated by linear splines
KTU_AAV_ABR = np.array([0, 0.25, 0.6, 1.0, 1.4])
KTU_VAL     = np.array([0, 0.30, 0.45, 0.52, 0.53])

def aav_over_abr(w, d, e):
    """Aav/Abr for a transverse load. Assumes the round end is concentric with the hole
    (radius e). t cancels out, so everything is per unit thickness.
      A1 = A4: cut from the 45-deg hole point to the straight edge -> w/2 - (D/2) sin45
      A2 = A3: radial section through the round end               -> e - D/2"""
    a1 = a4 = w / 2 - (d / 2) * np.sin(np.pi / 4)
    a2 = a3 = e - d / 2
    a_av = 6 / (3 / a1 + 1 / a2 + 1 / a3 + 1 / a4)
    return a_av / d   # Abr per unit thickness = D

def ktu_func(w, d, e):
    """Ktu from Aav/Abr; clamped to the chart (0-1.4)."""
    return np.interp(aav_over_abr(w, d, e), KTU_AAV_ABR, KTU_VAL)



#Areas
def bearing_area(d, t):  #Abr
    return d * t

def net_tension_area(w, d, t):  #At
    return (w - d) * t


### whatever
def sig_x(m_x, y, I_p):
    return (m_x * y) / I_p

def sig_y(f_y, w, d, t, k_e):
    return (0.5 * f_y) / (k_e * net_tension_area(w, d, t))

def sig_z(f_z, l, w, I):
    length = np.arange(0, l, 0.01)
    return (f_z * 0.5 * length * 0.5 * w) / I


#failure formulas hole
def sig_t_max(Fy, w, d, t, kt):  #Maximum Tensile Stress
    return Fy / (kt * net_tension_area(w, d, t))

def sig_br_max(Ftu, d, t, kbru):  #Shear Out Bearing
    return Ftu / (kbru * bearing_area(d, t))

def sig_cy_max(Fbry, d, t):  #Bushing Yield
    return Fbry / (1.85 * bearing_area(d, t))

def sig_ty_max(Fu, d, t, kbry):  #Bolt Shear Strength
    return Fu / (kbry * bearing_area(d, t))

def sig_tu_max(Ftu, d, t, ktu):  #Bolt Bending Strength
    return Ftu / (ktu * bearing_area(d, t))

#failure formulas root: the lug is a cantilever of length l from its base, loaded at the hole centre
def sig_bending_root(f_z, m_x, l, w, t):  #In-plane bending at the root from the transverse load and M_x
    M = f_z * l + abs(m_x)    # bending moment at the root: f_z on its lever arm + applied moment (worst case: same sign)
    c = w / 2                 # distance from the neutral axis to the outer edge
    I = t * w**3 / 12         # second moment of area of the root section (bending in the lug plane)
    return M * c / I

def sig_axial_root(f_y, w, t):  #Axial stress at the root from the axial load
    return f_y / (w * t)

def tau_shear_root(f_z, w, t):  #Peak transverse shear stress at the root (rectangle: 1.5 x average)
    return 1.5 * f_z / (w * t)

def sig_von_mises(sigma, tau):  #Equivalent stress from a normal and a shear stress
    return np.sqrt(sigma**2 + 3 * tau**2)

def mass(t, l, w, d, rho):
    # rectangle from base to hole centre + half-disc round end (radius w/2) - hole
    return ((l * w) + 0.5 * np.pi * (0.5 * w)**2 - np.pi * (0.5 * d)**2) * t * rho

#Find Optimal w, t, d so that sigma_y is just satisfied.

#design space:

# All in metres. 
t_list = np.arange(0.05e-3, 3e-3, 0.05e-3)   # thickness       0.05 - 3 mm, step 0.05 mm
l_list = np.arange(1e-3, 50e-3, 1e-3)        # length          1 - 50 mm,  step 1 mm (mass only)
w_list = np.arange(1e-3, 60e-3, 0.5e-3)      # width           1 - 60 mm,  step 0.5 mm
d_list = np.arange(1e-3, 30e-3, 0.5e-3)      # hole diameter   1 - 30 mm,  step 0.5 mm

# Grid over (w, d, t). l is not a separate variable: it follows from d.
# sparse=True keeps each axis as a thin array; stresses broadcast only over the
# axes they depend on, so memory stays small. Indexing is [i_w, i_d, i_t].
W, D, T = np.meshgrid(w_list, d_list, t_list, indexing='ij', sparse=True)
E = W / 2          # round-ended lug: outer radius e is fixed at half the width
L = l_over_d * D   # base to hole centre is fixed at l_over_d hole diameters

with np.errstate(divide='ignore', invalid='ignore'):
    sigst  = sig_t_max(f_y, W, D, T, kt_func(W / D))                    # [w, d, t]
    sigsbr = sig_br_max(Ftu, D, T, kbru_func(E / D, D / T, T))          # [w, d, t]
    sigscy = sig_cy_max(Fbry, D, T)                                     # [1, d, t]
    #sigsty = sig_ty_max(Fu, D, T, kbry_func(E / D, T / D))             # [w, d, t]
    #sigstu = sig_tu_max(Ftu, D, T, ktu_func(W, D, E))                  # [w, d, t]

    sigbend = sig_bending_root(f_z, m_x, L, W, T)                       # [w, d, t]
    sigax   = sig_axial_root(f_y, W, T)                                 # [w, 1, t]
    tauroot = tau_shear_root(f_z, W, T)                                 # [w, 1, t]
    # Conservative: peak bending (outer edge) and peak shear (centre) are combined as if at the same point
    sigroot = sig_von_mises(sigbend + sigax, tauroot)                   # [w, d, t]

# --- Feasibility: every stress x SF x FF must stay below yield ---
# W > D is required: otherwise the net tension area is <= 0 and sigst comes out
# negative, which would wrongly count as "below yield". (With e = w/2 this also keeps e > d/2.)
# L - D/2 >= gap_min leaves room between the hole and the base (and keeps mass() positive).
# D >= d_bolt_min and T >= t_manuf are the smallest bolt and the thinnest plate we can use.
# The root check uses the von Mises stress of bending + axial + shear at the base of the lug.

k = SF * FF
feasible = ((W > D)                                                 # hole narrower than the lug
            & (L - D / 2 >= gap_min)                                    # gap between hole edge and base
            & (D >= d_bolt_min)                                         # minimum bolt size
            & (T >= t_manuf)                                            # minimum manufacturable thickness
            & np.isclose(W / D, 3)                                      # fixed width-to-hole ratio
            & (k * sigst < sigma_y) & (k * sigsbr < sigma_y) & (k * sigscy < sigma_y)
            & (k * sigroot < sigma_y))                                  # root: bending + axial + shear
            # & (k * sigsty < sigma_y) & (k * sigstu < sigma_y))        # excluded

# Heatmap over (w, d): smallest t that passes every check
t_min = np.full((len(w_list), len(d_list)), np.nan)
for i_w in range(len(w_list)):
    for i_d in range(len(d_list)):
        i_t = np.nonzero(feasible[i_w, i_d])[0]    # indices of all working t, smallest first
        if len(i_t) > 0:
            t_min[i_w, i_d] = t_list[i_t[0]]

# Mass of that thinnest lug for each (w, d). Thicker is always heavier, so t_min gives the lightest lug.
mass_min = mass(t_min, l_over_d * d_list[None, :], w_list[:, None], d_list[None, :], rho)    # [w, d]

# --- Optimum: lightest lug over the whole design space ---
if np.all(np.isnan(mass_min)):
    raise SystemExit("No design passes all checks: widen the design space (t_list, w_list, d_list) "
                     "or relax a limit / check the loads.")
i_w_opt, i_d_opt = np.unravel_index(np.nanargmin(mass_min), mass_min.shape)
w_opt = w_list[i_w_opt]
d_opt = d_list[i_d_opt]
t_opt = t_min[i_w_opt, i_d_opt]
e_opt = w_opt / 2
l_opt = l_over_d * d_opt
print(f"Optimum: w = {w_opt*1e3:.2f} mm, d = {d_opt*1e3:.2f} mm, t = {t_opt*1e3:.2f} mm, l = {l_opt*1e3:.2f} mm, "
      f"e = {e_opt*1e3:.2f} mm, mass = {mass_min[i_w_opt, i_d_opt]*1e3:.3f} g")

# Margin of safety per check at the optimum: MS = sigma_y / (SF * FF * sigma) - 1  (>= 0 is OK)
stresses_opt = {
    'Maximum tensile stress': sig_t_max(f_y, w_opt, d_opt, t_opt, kt_func(w_opt / d_opt)),
    'Shear out bearing':      sig_br_max(Ftu, d_opt, t_opt, kbru_func(e_opt / d_opt, d_opt / t_opt, t_opt)),
    'Bushing yield':          sig_cy_max(Fbry, d_opt, t_opt),
    'Bolt shear strength':    sig_ty_max(Fu, d_opt, t_opt, kbry_func(e_opt / d_opt, t_opt / d_opt)),
    'Bolt bending strength':  sig_tu_max(Ftu, d_opt, t_opt, ktu_func(w_opt, d_opt, e_opt)),
    'Root (von Mises)':       sig_von_mises(sig_bending_root(f_z, m_x, l_opt, w_opt, t_opt) + sig_axial_root(f_y, w_opt, t_opt),
                                            tau_shear_root(f_z, w_opt, t_opt)),
}
for name, sigma in stresses_opt.items():
    MS = sigma_y / (SF * FF * sigma) - 1
    print(f"  {name:24s} sigma = {sigma/1e6:7.1f} MPa   MS = {MS:6.2f}")
print(f"  root parts: bending = {sig_bending_root(f_z, m_x, l_opt, w_opt, t_opt)/1e6:.1f} MPa, "
      f"axial = {sig_axial_root(f_y, w_opt, t_opt)/1e6:.1f} MPa, shear = {tau_shear_root(f_z, w_opt, t_opt)/1e6:.1f} MPa")

# Colour scheme: green = small (light, good), amber = middle, red = large (heavy, bad).
# Grey = no t in the design space works for that (w, d).
good_to_bad = LinearSegmentedColormap.from_list('good_to_bad', ['#0ca30c', '#fab219', '#d03b3b'])
good_to_bad.set_bad('#d9d9d6')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
for ax, val, label in [(ax1, t_min * 1e3, 'minimum t [mm]'), (ax2, mass_min * 1e3, 'mass at minimum t [g]')]:
    im = ax.pcolormesh(d_list * 1e3, w_list * 1e3, val, shading='auto', cmap=good_to_bad)
    fig.colorbar(im, ax=ax, label=label)
    ax.plot(d_opt * 1e3, w_opt * 1e3, marker='*', markersize=16, color='black', linestyle='none', label='lightest lug')
    ax.set_xlabel('d [mm]')
    ax.set_ylabel('w [mm]  (e = w/2)')
    ax.legend(loc='lower right')
ax1.set_title('Thinnest lug passing all checks')
ax2.set_title(f'Lug mass (rho = {rho}, l = {l_over_d} d)')
fig.suptitle(f'SF = {SF}, FF = {FF}   (green = good, red = bad, grey = no design works)')
plt.tight_layout()
plt.show()
