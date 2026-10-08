"""
Plots for attitude_sim.py. Running this file runs the sim (on import) and saves three figures
to figures/, as PNG and PDF, without titles (the report captions carry those):
  1. disturbance_torques     - each torque source around the orbit (log scale)
  2. attitude_response.png    - total torque, accumulated momentum and pointing error per axis
  3. orbit_map.png            - total torque painted onto the first orbit
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.patches import Rectangle, Wedge, FancyArrowPatch, Patch
from matplotlib.ticker import MultipleLocator, LogLocator, NullFormatter
from matplotlib.transforms import blended_transform_factory
from scipy.spatial.transform import Rotation as Rot

import constants as C
import attitude_sim as sim

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
TEXT_WIDTH = 6.3   # [in] report text width (A4, 2.5 cm margins); LaTeX: 	he	extwidth / 72.27

# ---------- Style (light chart surface, validated categorical order) ----------
SURFACE  = "#fcfcfb"
INK      = "#0b0b0b"
INK_2    = "#52514e"
MUTED    = "#898781"
GRID     = "#e1e0d9"
BASELINE = "#c3c2b7"
SHADOW   = "#f0efec"
SERIES   = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]
BLUE_RAMP = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
LW = 1.1   # data lines [pt] at print size

plt.rcParams.update({
    "font.family": ["Segoe UI", "DejaVu Sans"],
    "mathtext.default": "regular",
    "font.size": 8,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "axes.edgecolor": BASELINE,
    "axes.linewidth": 0.6,
    "axes.labelcolor": INK_2,
    "axes.labelsize": 8,
    "axes.titlecolor": INK,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "axes.grid.axis": "y",
    "axes.axisbelow": True,
    "grid.color": GRID,
    "grid.linewidth": 0.5,
    "xtick.color": BASELINE,
    "ytick.color": BASELINE,
    "xtick.labelcolor": MUTED,
    "ytick.labelcolor": MUTED,
    "xtick.major.size": 2.5,
    "ytick.major.size": 0,
    "xtick.minor.size": 1.5,
    "legend.frameon": False,
    "legend.fontsize": 7.5,
    "legend.labelcolor": INK_2,
    "lines.solid_capstyle": "round",
    "lines.solid_joinstyle": "round",
    "savefig.dpi": 300,
    "savefig.facecolor": SURFACE,
})

# ---------- Data ----------
orbit = sim.n_log / (2 * np.pi)                     # orbits since start
period_min = 2 * np.pi / sim.dn / 60                # [min]
AXES = ["Pitch (X)", "Roll (Y)", "Yaw (Z)"]

# error as a rotation away from perfect nadir pointing
error_rot = Rot.from_rotvec(sim.error_log)
error_deg = np.degrees(np.unwrap(error_rot.as_euler("XYZ"), axis=0))      # per axis, continuous
z_axis = error_rot.apply([0.0, 0.0, 1.0])                                  # body Z in the nadir frame
off_nadir = np.degrees(np.arccos(np.clip(z_axis[:, 2], -1, 1)))           # how far Z is off Mercury
momentum = np.cumsum(sim.T_log, axis=0) * sim.dt                           # [N m s]

# eclipse spans as (start, end) in orbits
_e = np.r_[False, sim.eclipse_log.astype(bool), False].astype(int)
_starts, _ends = np.flatnonzero(np.diff(_e) == 1), np.flatnonzero(np.diff(_e) == -1) - 1
ECLIPSES = [(orbit[a], orbit[b]) for a, b in zip(_starts, _ends)]


# ---------- Helpers ----------
ECLIPSE_KEY = Patch(fc=SHADOW, ec=BASELINE, lw=0.5)   # legend swatch for the shaded bands


def shade_eclipses(ax):
    for a, b in ECLIPSES:
        ax.axvspan(a, b, color=SHADOW, lw=0, zorder=0)


def orbit_axis(ax, label=True):
    ax.set_xlim(0, orbit[-1])
    ax.xaxis.set_major_locator(MultipleLocator(1))
    ax.xaxis.set_minor_locator(MultipleLocator(0.25))
    ax.grid(axis="x", which="major", color=GRID, lw=0.5)
    if label:
        ax.set_xlabel(f"Orbits since start  (1 orbit = {period_min:.0f} min)")
    else:
        ax.tick_params(axis="x", labelbottom=False)


def spread(values, gap):
    """Nudge sorted label positions apart by at least `gap`, keeping their mean."""
    values = np.asarray(values, float)
    order = np.argsort(values)
    placed = values[order].copy()
    for k in range(1, len(placed)):
        placed[k] = max(placed[k], placed[k - 1] + gap)
    placed += values[order].mean() - placed.mean()
    out = np.empty_like(placed)
    out[order] = placed
    return out


def end_labels(ax, ys, texts, colors, gap_frac=0.13):
    """Direct labels in the right margin, with a thin leader when a label had to move."""
    lo, hi = ax.get_ylim()
    placed = spread(ys, gap_frac * (hi - lo))
    trans = blended_transform_factory(ax.transAxes, ax.transData)
    for y, yp, text, color in zip(ys, placed, texts, colors):
        ax.plot(orbit[-1], y, "o", ms=4.5, color=color, mec=SURFACE, mew=1.0, zorder=6, clip_on=False)
        ax.annotate(text, xy=(1.0, y), xycoords=trans, xytext=(1.03, yp), textcoords=trans,
                    va="center", ha="left", color=INK_2, fontsize=7.5, annotation_clip=False,
                    arrowprops=dict(arrowstyle="-", color=BASELINE, lw=0.5, shrinkA=1, shrinkB=4)
                    if abs(yp - y) > 0.02 * (hi - lo) else None)


def at(o):
    """Index of the sample closest to orbit o."""
    return int(np.argmin(np.abs(orbit - o)))


def low(values, a, b):
    """Index of the smallest value between orbits a and b."""
    idx = np.flatnonzero((orbit >= a) & (orbit <= b))
    return idx[np.nanargmin(values[idx])]


def tag(ax, letter, xy, xytext=None):
    """[a]-style reference label for the report text, with a thin leader when placed off the feature."""
    ax.annotate(f"[{letter}]", xy=xy, xytext=xy if xytext is None else xytext,
                ha="center", va="center", fontsize=7.5, fontweight="bold", color=INK, zorder=8,
                bbox=dict(boxstyle="round,pad=0.15", fc=SURFACE, ec="none", alpha=0.85),
                arrowprops=None if xytext is None else
                dict(arrowstyle="-", color=MUTED, lw=0.5, shrinkA=0, shrinkB=2))


# ---------- 1. Disturbance torques by source ----------
def plot_torques():
    fig, ax = plt.subplots(figsize=(TEXT_WIDTH, 3.1))
    fig.subplots_adjust(left=0.1, right=0.98, top=0.85, bottom=0.14)

    shade_eclipses(ax)
    names = list(sim.torque_arrays)
    mags = {}
    for i, name in enumerate(names):
        mag = np.linalg.norm(sim.torque_arrays[name], axis=1)
        mag[mag == 0] = np.nan                    # Sun off in eclipse, no albedo at night
        mags[name] = mag
        ax.plot(orbit, mag, color=SERIES[i], lw=LW, label=name, zorder=3)
    ax.set_yscale("log")
    finite = np.concatenate([m[np.isfinite(m)] for m in mags.values()])
    ax.set_ylim(10 ** np.floor(np.log10(finite.min())), 10 ** np.ceil(np.log10(finite.max())))
    ax.yaxis.set_major_locator(LogLocator(base=10, numticks=12))
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.set_ylabel("Torque magnitude [N·m]")
    orbit_axis(ax)

    # where the spacecraft is during the first orbit
    top = blended_transform_factory(ax.transData, ax.transAxes)
    for x, text in [(0.25, "north pole"), (0.5, "noon"), (0.75, "south pole")]:
        ax.text(x, 1.015, text, transform=top, ha="center", va="bottom", fontsize=7, color=MUTED)

    # reference labels for the report text
    gg, srp, alb = mags["Gravity gradient"], mags["Solar radiation"], mags["Planet albedo+IR"]
    mag, th = mags["Magnetic"], mags["Thermal"]
    i = at(0.06)
    tag(ax, "a", (orbit[i], gg[i]), (orbit[i], gg[i] * 8))                     # GG starts tiny
    i = np.flatnonzero((orbit > ECLIPSES[0][1]) & (gg > 1e-5))[0]
    tag(ax, "b", (orbit[i], gg[i]), (orbit[i] - 0.08, gg[i] * 4))              # GG jumps after tilt
    i = low(mag, 0.2, 0.3)
    tag(ax, "c", (orbit[i], mag[i]), (orbit[i] + 0.07, mag[i] * 3))            # magnetic dip at pole
    a, b = ECLIPSES[1]
    tag(ax, "d", ((a + b) / 2, 1e-6))                                       # no SRP in eclipse
    i = np.flatnonzero(np.isfinite(alb) & (orbit < 0.8))[-1]
    tag(ax, "e", (orbit[i] + 0.035, 1e-6))                                     # albedo off at terminator
    i = low(srp, 0.7, 0.86)
    tag(ax, "f", (orbit[i], srp[i]), (orbit[i], srp[i] / 5))                  # SRP near-cancellation
    i = at(2.0)
    tag(ax, "g", (orbit[i], th[i]), (orbit[i], th[i] * 3.5))                   # thermal constant
    i = low(gg, 0.9, 1.0)
    tag(ax, "h", (orbit[i], gg[i]), (orbit[i] + 0.06, gg[i] / 5))              # GG dip near nadir

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles + [ECLIPSE_KEY], labels + ["Eclipse"], loc="upper left",
               bbox_to_anchor=(0.1, 1.0), ncol=len(names) + 1, handlelength=1.6, columnspacing=1.8)
    return fig


# ---------- 2. Attitude response ----------
def plot_response():
    fig, axs = plt.subplots(4, 1, figsize=(TEXT_WIDTH, 6.9), sharex=True,
                            gridspec_kw=dict(hspace=0.55, left=0.1, right=0.84, top=0.92, bottom=0.07))
    i10 = np.argmax(off_nadir > 10)

    panels = [
        (sim.T_log * 1e6, "Total disturbance torque", "[µN·m]", lambda v: f"{v:+.0f}"),
        (momentum, "Accumulated momentum", "[N·m·s]",
         lambda v: f"{v:+.2f}"),
        (error_deg, "Deviation from the nadir-tracking attitude", "[°]", lambda v: f"{v:+.0f}°"),
    ]
    for ax, (data, title, unit, fmt) in zip(axs, panels):
        shade_eclipses(ax)
        ax.axhline(0, color=BASELINE, lw=0.6, zorder=1)
        for k in range(3):
            ax.plot(orbit, data[:, k], color=SERIES[k], lw=LW, label=AXES[k], zorder=3)
        ax.set_title(title, loc="left", fontsize=8.5, fontweight="bold", pad=5)
        ax.set_ylabel(unit)
        orbit_axis(ax, label=False)
        end_labels(ax, data[-1], [f"{AXES[k].split()[0]}  {fmt(data[-1, k])}" for k in range(3)], SERIES[:3])
    axs[2].yaxis.set_major_locator(MultipleLocator(360))

    # off-nadir angle: the single number that matters for pointing
    ax = axs[3]
    shade_eclipses(ax)
    ax.axhline(10, color=BASELINE, lw=0.6, zorder=1)
    ax.text(0.005, 10, "10°", transform=blended_transform_factory(ax.transAxes, ax.transData),
            ha="left", va="bottom", fontsize=7, color=MUTED)
    ax.plot(orbit, off_nadir, color=INK, lw=LW, zorder=3)
    ax.plot(orbit[i10], 10, "o", ms=5, color=INK, mec=SURFACE, mew=1.2, zorder=6)
    ax.annotate(f"[j]  10° off after {orbit[i10] * period_min:.0f} min", xy=(orbit[i10], 10),
                xytext=(0.06, 125), fontsize=7.5, color=INK_2, va="center", ha="left",
                arrowprops=dict(arrowstyle="-", color=BASELINE, lw=0.5, shrinkA=2, shrinkB=5))
    ax.set_ylim(0, 180)
    ax.yaxis.set_major_locator(MultipleLocator(45))
    ax.set_title("Angle between the Z axis and Mercury", loc="left", fontsize=8.5,
                 fontweight="bold", pad=5)
    ax.set_ylabel("[°]")
    orbit_axis(ax)

    # reference labels for the report text
    i = at(1.5)
    tag(axs[2], "i", (orbit[i], error_deg[i, 2]), (orbit[i] + 0.12, error_deg[i, 2] - 220))  # yaw spin-up
    i = low(off_nadir, 0.85, 1.1)
    tag(axs[3], "k", (orbit[i], off_nadir[i]), (orbit[i], 45))                  # swings back near nadir

    handles, labels = axs[0].get_legend_handles_labels()
    fig.legend(handles + [ECLIPSE_KEY], labels + ["Eclipse"], loc="upper left",
               bbox_to_anchor=(0.1, 1.0), ncol=4, handlelength=1.6, columnspacing=1.8)
    return fig


# ---------- 3. Orbit map ----------
def plot_orbit_map():
    R, r = C.MERCURY_RADIUS / 1e6, sim.r / 1e6           # [1000 km]
    first = orbit <= 1
    n = sim.n_log[first]
    x, y = -r * np.cos(n), r * np.sin(n)                 # Sun to the right (+x), north up (+y)
    total = np.linalg.norm(sim.T_log[first], axis=1) * 1e6

    fig, ax = plt.subplots(figsize=(0.5 * TEXT_WIDTH, 3.25))
    fig.subplots_adjust(left=0.0, right=1.0, top=1.0, bottom=0.13)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-4.9, 5.4)
    ax.set_ylim(-4.0, 4.0)

    # shadow cylinder, planet with a day and night half
    ax.add_patch(Rectangle((-6, -R), 6, 2 * R, color=SHADOW, lw=0, zorder=0))
    ax.add_patch(Wedge((0, 0), R, 90, 270, fc="#d6d5ce", ec="none", zorder=1))
    ax.add_patch(Wedge((0, 0), R, -90, 90, fc="#ecebe6", ec="none", zorder=1))
    ax.text(0, 0.18, "Mercury", ha="center", va="center", fontsize=9, color=INK_2, zorder=2)
    ax.text(-R / 2, -0.45, "night", ha="center", fontsize=7, color=MUTED, zorder=2)
    ax.text(R / 2, -0.45, "day", ha="center", fontsize=7, color=MUTED, zorder=2)
    ax.text(-4.85, -R - 0.12, "Mercury's shadow", ha="left", va="top", fontsize=7, color=MUTED)

    # sunlight
    for yy in (-2.2, -1.1, 1.1, 2.2):
        ax.add_patch(FancyArrowPatch((5.3, yy), (4.25, yy), arrowstyle="-|>", mutation_scale=6,
                                     color=BASELINE, lw=0.7))
    ax.text(4.78, 3.05, "Sunlight", ha="center", fontsize=7.5, color=MUTED)

    # torque ring
    cmap = LinearSegmentedColormap.from_list("blue", BLUE_RAMP)
    pts = np.column_stack((x, y)).reshape(-1, 1, 2)
    ring = LineCollection(np.concatenate([pts[:-1], pts[1:]], axis=1), cmap=cmap,
                          norm=Normalize(0, total.max()), lw=5, capstyle="butt", zorder=3)
    ring.set_array(total[:-1])
    ax.add_collection(ring)

    # landmarks and direction of travel
    ax.plot(x[0], y[0], "o", ms=6, color=INK, mec=SURFACE, mew=1.3, zorder=5)
    ax.text(x[0] - 0.35, y[0], "start", ha="right", va="center", fontsize=7.5, color=INK_2)
    arc = np.linspace(0.03, 0.11, 30) * 2 * np.pi
    ax.add_patch(FancyArrowPatch((-(r + 0.45) * np.cos(arc[0]), (r + 0.45) * np.sin(arc[0])),
                                 (-(r + 0.45) * np.cos(arc[-1]), (r + 0.45) * np.sin(arc[-1])),
                                 connectionstyle="arc3,rad=-0.12", arrowstyle="-|>",
                                 mutation_scale=7, color=MUTED, lw=0.7))
    ax.text(0, r + 0.35, "north pole", ha="center", va="bottom", fontsize=7.5, color=INK_2)
    ax.text(0, -r - 0.35, "south pole", ha="center", va="top", fontsize=7.5, color=INK_2)
    ax.text(r + 0.3, 0, "noon", ha="left", va="center", fontsize=7.5, color=INK_2)

    i_max = np.argmax(total)
    ax.plot(x[i_max], y[i_max], "o", ms=6, color=BLUE_RAMP[-1], mec=SURFACE, mew=1.3, zorder=5)
    out = 1 + 0.75 / r
    side = 1 if x[i_max] >= 0 else -1
    ax.annotate(f"peak {total[i_max]:.0f} µN·m", xy=(x[i_max], y[i_max]),
                xytext=(x[i_max] * out + 0.1 * side, y[i_max] * out), fontsize=7.5, color=INK_2,
                ha="left" if side > 0 else "right", va="center",
                arrowprops=dict(arrowstyle="-", color=BASELINE, lw=0.5, shrinkA=2, shrinkB=6))

    cax = fig.add_axes([0.15, 0.09, 0.7, 0.022])
    cbar = fig.colorbar(ring, cax=cax, orientation="horizontal")
    cbar.outline.set_visible(False)
    cbar.ax.tick_params(length=0, labelcolor=MUTED)
    cbar.set_label("Total disturbance torque [µN·m]", color=INK_2, fontsize=8)
    return fig


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    for name, make in [("disturbance_torques", plot_torques), ("attitude_response", plot_response),
                       ("orbit_map", plot_orbit_map)]:
        fig = make()
        for ext in ("png", "pdf"):      # PDF is vector, sharper in a report
            fig.savefig(os.path.join(OUT_DIR, f"{name}.{ext}"), bbox_inches="tight", pad_inches=0.05)
    plt.show()
