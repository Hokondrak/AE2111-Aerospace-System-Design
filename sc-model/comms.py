import numpy as np
import constants as C

### Communications subsystem: first-level parametric sizing
# Two architectures from the COMMS chapter (tab:architecture_comparison), both with a
# parabolic HGA. Link budget per the ADSEE II formula sheet:
#   Eb/N0 = EIRP - L_fs - L_x + G/T - 10 log10(k_B * R)
# Output per architecture: antenna dimensions, RF/DC power, modulation/coding,
# required pointing accuracy, data budget, mass/volume, plus design checks.
# All losses below are positive dB values that get subtracted.


# ---------- Mission geometry ----------
D_EARTH_MAX = C.EARTH_APHELION + C.MERCURY_APHELION    # m, 1.483 AU, sizing case
D_EARTH_MIN = C.EARTH_PERIHELION - C.MERCURY_APHELION  # m, 0.517 AU
# (R_Mercury + h) is ~3000 km, negligible next to 0.5-1.5 AU, so it is left out.

# ---------- Orbit: same values as eps.py ----------
ORBITAL_PERIOD = 7630              # s
EARTH_OCCULTATION = 2118           # s, Earth hidden behind Mercury per orbit
MAX_ECLIPSE_DURATION = 2115.2      # s
EARTH_VISIBLE = ORBITAL_PERIOD - EARTH_OCCULTATION  # s, downlink possible (MER-COMMS-030)


# ---------- Requirements ----------
REQ_DOWNLINK_RATE = {"Ka": 316e3, "X": 324.5e3}  # bit/s, MER-COMMS-010
REQ_BER = 1e-5                     # MER-COMMS-110
REQ_LINK_MARGIN = 3.0              # dB, MER-COMMS-120 (read as: AT LEAST 3 dB)
REQ_POINTING = 360 / 3600          # deg, MER-COMMS-130, 360 arcsec HGA pointing error
FAIRING_DIAMETER = 4.6             # m, MER-COMMS-720, Ariane 6 usable fairing diameter

USE_DATA_BUDGET = False  # True: size on the data budget below instead of MER-COMMS-010


# ---------- Architectures (tab:architecture_comparison) ----------
# The table says Ka = 35 GHz and X = 12 GHz. 12 GHz is not X-band; the deep-space
# downlink allocations are 8.40-8.45 GHz (X) and 31.8-32.3 GHz (Ka), used here.
ARCHITECTURES = {
    "Arch 1": dict(band="Ka", modulation="QPSK",  coding="LDPC r=1/2",  D=3.0, P_RF=60.0),
    "Arch 2": dict(band="X",  modulation="8-PSK", coding="Turbo r=1/2", D=3.0, P_RF=60.0),
}

DOWNLINK_FREQ = {"X": 8.42e9, "Ka": 32.0e9}      # Hz
BAND_ALLOCATION = {"X": 50e6, "Ka": 500e6}       # Hz, width of the deep-space allocation


# ---------- Modulation and coding ----------
# Modulation: (Eb/N0 for BER 1e-5 uncoded [dB], bandwidth efficiency [bit/s/Hz]),
# tab:modulation_efficiency.
MODULATIONS = {
    "BPSK":  (9.6, 1.0),
    "QPSK":  (9.6, 2.0),
    "8-PSK": (13.0, 3.0),
}
# Coding: (coding gain [dB], code rate [-]); low end of tab:fec_comparison (conservative).
CODINGS = {
    "Uncoded":     (0.0, 1.0),
    "Conv r=1/2":  (5.0, 1 / 2),
    "Turbo r=1/2": (8.5, 1 / 2),
    "LDPC r=1/2":  (9.0, 1 / 2),
}
IMPLEMENTATION_LOSS = 1.0  # dB, demodulator/decoder losses on top of the ideal curves


# ---------- Link budget inputs ----------
ANTENNA_EFF = 0.6          # -> 18.19 in G = 20 log D + 20 log f[GHz] + 18.19
TX_LOSS = -10 * np.log10(0.8)   # dB, L_t (loss factor 0.8)
RX_LOSS = -10 * np.log10(0.8)   # dB, L_r (loss factor 0.8)
ATMOS_LOSS = {"X": 0.5, "Ka": 1.0}  # dB, L_a; Ka is more weather-sensitive (report used 0.5)

GS_DIAMETER = 35.0         # m, ESA deep-space antenna (Cebreros/Malargue/New Norcia)
GS_POINTING = 0.003        # deg, ground-station pointing error
GS_G_OVER_T = {"X": 51.0, "Ka": 55.8}  # dB/K, ESA DSA spec (Vassallo)
GS_TX_POWER = 20e3         # W, DSA X-band uplink transmitter

# Uplink / telecommand: X-band on both architectures (MER-COMMS-050)
UPLINK_FREQ = DOWNLINK_FREQ["X"] * 749 / 880  # Hz, X-band turnaround ratio -> 7.17 GHz
TC_RATE = 2e3              # bit/s, nominal telecommand rate through the HGA
SC_NOISE_TEMP = 500        # K, S/C receiver system noise temperature, ASSUMPTION (hot Mercury in view)
LGA_GAIN = 0.0             # dBi, low-gain antenna at edge of coverage (safe mode)

BOLTZMANN_DB = 10 * np.log10(C.BOLTZMANN)  # dB(J/K), -228.6


# ---------- Data budget ----------
# (name, data rate while active after compression [bit/s], duty cycle [-]).
# Duty cycles as in eps.py. RATES ARE PLACEHOLDERS: replace with the report-1 values.
INSTRUMENTS = [
    ("HSRC (camera)",   1.0e6, 0.20),
    ("UVS",             50e3,  0.25),
    ("MAG",             2e3,   1.00),
    ("Laser altimeter", 15e3,  MAX_ECLIPSE_DURATION / ORBITAL_PERIOD),  # on in eclipse
    ("Housekeeping",    2e3,   1.00),
]
PACKET_OVERHEAD = 0.05     # fraction, CCSDS packet/frame headers

# Solar conjunction: no link while the Sun-Earth-Probe angle is below SEP_MIN.
SEP_MIN = {"Ka": 2.0, "X": 3.0}  # deg, ASSUMPTION; the corona disturbs Ka less than X
# Near superior conjunction SEP ~ r_M * phi / (1 AU + r_M), phi grows 360 deg per synodic period
MERCURY_SMA = (C.MERCURY_PERIHELION + C.MERCURY_APHELION) / 2  # m
SEP_RATE = MERCURY_SMA / (C.AU + MERCURY_SMA) * 360 / C.MERCURY_SYNODIC_PERIOD  # deg/s


# ---------- Hardware sizing (ADSEE I notes, SMAD) ----------
ANTENNA_AREAL_MASS = 3.0   # kg/m², reflector incl. high-temperature coating (rho_ant)
F_OVER_D = 0.4             # -, reflector focal ratio, sets the dish depth
TRANS_SPECIFIC_POWER = 20  # W/kg, transceiver (P_sp)
TRANS_DENSITY = 1000       # kg/m³, transceiver (rho_trans)
TWTA_EFF = 0.5             # -, RF out / DC in, TWT + EPC

# ---------- Power allocation (eps.py) ----------
COMMS_POWER_ALLOC = 100    # W, eps.py COMMpower_data, during downlink
RECEIVER_POWER = 10        # W, eps.py COMMpower_telemetry, transponder always on
P_RF_MAX = (COMMS_POWER_ALLOC - RECEIVER_POWER) * TWTA_EFF  # W, RF power the EPS can feed

MASS_MARGIN = 0.20         # same as eps.py


# =====================================================================
# MODEL
# =====================================================================
def gain(D, f):
    """Parabolic antenna gain [dBi], diameter D [m], frequency f [Hz]."""
    return 10 * np.log10(ANTENNA_EFF * (np.pi * D * f / C.SPEED_OF_LIGHT) ** 2)


def beamwidth(D, f):
    """Half-power beamwidth alpha_1/2 = 21 / (f[GHz] D) [deg]."""
    return 21 / (f / 1e9 * D)


def pointing_loss(e, D, f):
    """L_pr = 12 (e / alpha_1/2)^2 [dB]; only valid inside the main lobe (e <= alpha/2)."""
    return 12 * (e / beamwidth(D, f)) ** 2


def optimal_diameter(e, f):
    """Diameter [m] maximising G - L_pr for pointing error e. Gain grows with
    20 log D but L_pr with D^2, so above this a bigger dish LOSES dB (L_pr = 4.3 dB here)."""
    return 21 / (f / 1e9 * e) * np.sqrt(20 / (24 * np.log(10)))


def free_space_loss(d, f):
    """L_fs = 20 log10(4 pi d / lambda) [dB]."""
    return 20 * np.log10(4 * np.pi * d * f / C.SPEED_OF_LIGHT)


def required_eb_n0(modulation, coding):
    """Eb/N0 [dB] for BER 1e-5 after coding, incl. implementation loss."""
    return MODULATIONS[modulation][0] - CODINGS[coding][0] + IMPLEMENTATION_LOSS


def bandwidth(rate, modulation, coding):
    """Occupied bandwidth [Hz]: coded symbols cost 1/r more, B = R / (r eta_BW)."""
    return rate / (CODINGS[coding][1] * MODULATIONS[modulation][1])


def downlink(band, D, P_RF, rate, d=D_EARTH_MAX, e=REQ_POINTING):
    """Downlink budget terms [dB]. Works on numpy arrays of D / P_RF too."""
    f = DOWNLINK_FREQ[band]
    G_t = gain(D, f)
    eirp = 10 * np.log10(P_RF) + G_t - TX_LOSS
    L_fs = free_space_loss(d, f)
    L_pr_sc = pointing_loss(e, D, f)
    L_pr_gs = pointing_loss(GS_POINTING, GS_DIAMETER, f)
    eb_n0 = (eirp - L_fs - L_pr_sc - L_pr_gs - ATMOS_LOSS[band] - RX_LOSS
             + GS_G_OVER_T[band] - BOLTZMANN_DB - 10 * np.log10(rate))
    return dict(G_t=G_t, EIRP=eirp, alpha_t=beamwidth(D, f),
                alpha_r=beamwidth(GS_DIAMETER, f), L_pr_sc=L_pr_sc,
                L_pr=L_pr_sc + L_pr_gs, L_fs=L_fs, eb_n0=eb_n0)


def downlink_rate_required(band):
    """Data budget: orbit-average generation -> rate needed while Earth is visible,
    stretched for the solar-conjunction blackout. Also returns the blackout storage."""
    generation = sum(rate * duty for _, rate, duty in INSTRUMENTS) * (1 + PACKET_OVERHEAD)  # bit/s
    blackout = 2 * SEP_MIN[band] / SEP_RATE                   # s per superior conjunction
    blackout_frac = blackout / C.MERCURY_SYNODIC_PERIOD
    rate = generation * ORBITAL_PERIOD / EARTH_VISIBLE / (1 - blackout_frac)  # bit/s
    storage = generation * blackout                           # bit, held through a conjunction
    return dict(generation=generation, blackout=blackout, blackout_frac=blackout_frac,
                rate=rate, storage=storage)


def hardware(D, P_RF):
    """Mass [kg], volume and power of the RF chain for antenna D [m] and RF power P_RF [W]."""
    antenna = ANTENNA_AREAL_MASS * np.pi * D ** 2 / 4
    twta = 0.013 * P_RF + 1.3
    transceiver = P_RF / TRANS_SPECIFIC_POWER
    total = antenna + twta + transceiver
    dc = P_RF / TWTA_EFF + RECEIVER_POWER
    return dict(antenna=antenna, twta=twta, transceiver=transceiver, total=total,
                total_margin=total * (1 + MASS_MARGIN),
                trans_volume=transceiver / TRANS_DENSITY,
                dish_depth=D / (16 * F_OVER_D),
                dc=dc, heat=dc - P_RF)


def ok(passed):
    return "OK  " if passed else "FAIL"


# =====================================================================
# DATA BUDGET
# =====================================================================
print("=" * 60)
print(" COMMS - DATA BUDGET")
print("=" * 60)
for name, rate, duty in INSTRUMENTS:
    print(f"  {name:20} {rate / 1e3:9.1f} kbps x {duty * 100:5.1f}%  = {rate * duty / 1e3:7.1f} kbps avg")
DATA = {band: downlink_rate_required(band) for band in ("Ka", "X")}
gen = DATA["Ka"]["generation"]
print(f"  Generation incl. {PACKET_OVERHEAD * 100:.0f}% overhead {gen / 1e3:9.1f} kbps")
print(f"  Volume per orbit       {gen * ORBITAL_PERIOD / 8e9:10.2f} GB")
print(f"  Volume per day         {gen * C.DAY / 8e9:10.2f} GB")
print(f"  Earth visible          {EARTH_VISIBLE / ORBITAL_PERIOD * 100:10.1f} % of the orbit")
print(f"  Occultation storage    {gen * EARTH_OCCULTATION / 8e9:10.2f} GB")
for band, data in DATA.items():
    print(f" {band}-band (SEP > {SEP_MIN[band]:.0f} deg)")
    print(f"  Conjunction blackout   {data['blackout'] / C.DAY:10.1f} days ({data['blackout_frac'] * 100:.1f}% of synodic period)")
    print(f"  Conjunction storage    {data['storage'] / 8e9:10.1f} GB")
    print(f"  Required downlink      {data['rate'] / 1e3:10.1f} kbps (MER-COMMS-010: {REQ_DOWNLINK_RATE[band] / 1e3:.1f} kbps)")
print("  (instrument rates are placeholders)")
print("=" * 60)

RATE = {band: DATA[band]["rate"] if USE_DATA_BUDGET else REQ_DOWNLINK_RATE[band]
        for band in ("Ka", "X")}


# =====================================================================
# MODULATION / CODING TRADE (baseline antenna and power)
# =====================================================================
print()
print("=" * 60)
print(" COMMS - MODULATION / CODING TRADE (baseline D, P_RF)")
print("=" * 60)
for name, arch in ARCHITECTURES.items():
    band, rate = arch["band"], RATE[arch["band"]]
    eb_n0 = downlink(band, arch["D"], arch["P_RF"], rate)["eb_n0"]
    print(f" {name} ({band}-band, {arch['D']} m, {arch['P_RF']:.0f} W, {rate / 1e3:.1f} kbps)")
    print(f"  {'':24} {'Req Eb/N0':>9} {'Margin':>8} {'B [kHz]':>9}")
    options = [(m, c) for m in MODULATIONS for c in CODINGS
               if bandwidth(rate, m, c) <= BAND_ALLOCATION[band]]
    # Highest margin; on a tie the narrower bandwidth
    best = max(options, key=lambda mc: (round(eb_n0 - required_eb_n0(*mc), 6), -bandwidth(rate, *mc)))
    for m, c in options:
        req = required_eb_n0(m, c)
        tag = " <- architecture" if (m, c) == (arch["modulation"], arch["coding"]) else ""
        tag += " <- best" if (m, c) == best else ""
        print(f"  {m + ' + ' + c:24} {req:9.1f} {eb_n0 - req:8.2f} {bandwidth(rate, m, c) / 1e3:9.1f}{tag}")
print("=" * 60)


# =====================================================================
# SIZING PER ARCHITECTURE
# =====================================================================
# Design point: RF power limited to what the EPS allocation can feed, antenna sized
# for >= 3 dB margin at max distance with the required pointing error. If no dish up
# to min(optimal, fairing) closes the link, the dish is capped and the power raised.
D_GRID = np.linspace(0.1, FAIRING_DIAMETER, 9000)  # m
RESULTS = {}

for name, arch in ARCHITECTURES.items():
    band, mod, cod = arch["band"], arch["modulation"], arch["coding"]
    f, rate = DOWNLINK_FREQ[band], RATE[band]
    req = required_eb_n0(mod, cod)

    D_opt = optimal_diameter(REQ_POINTING, f)
    D_cap = min(D_opt, FAIRING_DIAMETER)
    P_design = min(arch["P_RF"], P_RF_MAX)

    grid = D_GRID[D_GRID <= D_cap]
    margins = downlink(band, grid, P_design, rate)["eb_n0"] - req
    closes = margins >= REQ_LINK_MARGIN
    if closes.any():
        D_design = np.ceil(grid[closes][0] / 0.05) * 0.05  # round up to 5 cm
    else:
        D_design = np.floor(D_cap / 0.05) * 0.05
        margin = downlink(band, D_design, P_design, rate)["eb_n0"] - req
        P_design *= 10 ** ((REQ_LINK_MARGIN - margin) / 10)

    base = downlink(band, arch["D"], arch["P_RF"], rate)
    size = downlink(band, D_design, P_design, rate)

    # RF power that just closes the link with the baseline dish
    P_min_base = arch["P_RF"] * 10 ** ((REQ_LINK_MARGIN - (base["eb_n0"] - req)) / 10)

    # Largest pointing error that still leaves the required margin (main lobe: L_pr <= 3 dB)
    def pointing_required(budget, D):
        allowed = budget["eb_n0"] + budget["L_pr_sc"] - req - REQ_LINK_MARGIN  # dB
        if allowed <= 0:
            return "n/a (does not close)"
        e = beamwidth(D, f) * np.sqrt(min(allowed, 3.0) / 12) * 3600  # arcsec
        return f"{e:.0f} arcsec" + (" (main-lobe limit)" if allowed > 3.0 else "")

    hw_base = hardware(arch["D"], arch["P_RF"])
    hw = hardware(D_design, P_design)

    print()
    print("=" * 60)
    print(f" COMMS SIZING - {name.upper()} ({band}-band {f / 1e9:.2f} GHz, {mod} + {cod})")
    print("=" * 60)
    print(f"  {'':26} {'Baseline':>10} {'Sized':>10}")
    print(f"  {'Antenna diameter [m]':26} {arch['D']:10.2f} {D_design:10.2f}")
    print(f"  {'RF power [W]':26} {arch['P_RF']:10.1f} {P_design:10.1f}")
    print("Link budget (max distance, required pointing error)")
    for label, key, fmt in (("G_t [dBi]", "G_t", ".2f"), ("EIRP [dBW]", "EIRP", ".2f"),
                            ("alpha_1/2 t [deg]", "alpha_t", ".3f"), ("alpha_1/2 r [deg]", "alpha_r", ".4f"),
                            ("L_pr total [dB]", "L_pr", ".2f"), ("L_fs [dB]", "L_fs", ".2f"),
                            ("Eb/N0 [dB]", "eb_n0", ".2f")):
        print(f"  {label:26} {base[key]:10{fmt}} {size[key]:10{fmt}}")
    print(f"  {'Required Eb/N0 [dB]':26} {req:10.2f} {req:10.2f}")
    print(f"  {'Link margin [dB]':26} {base['eb_n0'] - req:10.2f} {size['eb_n0'] - req:10.2f}")
    print(f"  {'Bandwidth [kHz]':26} {bandwidth(rate, mod, cod) / 1e3:10.1f} {bandwidth(rate, mod, cod) / 1e3:10.1f}")
    print("Sizing limits")
    print(f"  Pointing-optimal dish  {D_opt:10.2f} m  (for {REQ_POINTING * 3600:.0f} arcsec)")
    print(f"  Fairing limit          {FAIRING_DIAMETER:10.2f} m")
    print(f"  RF power to close with {arch['D']} m: {P_min_base:6.1f} W")
    print(f"  RF power EPS can feed  {P_RF_MAX:10.1f} W  ({COMMS_POWER_ALLOC} W DC at {TWTA_EFF * 100:.0f}% TWTA eff.)")
    print("Required pointing accuracy (for >= 3 dB margin)")
    print(f"  Baseline               {pointing_required(base, arch['D'])}")
    print(f"  Sized                  {pointing_required(size, D_design)}")
    print(f"  (requirement MER-COMMS-130: {REQ_POINTING * 3600:.0f} arcsec)")
    print("Hardware")
    print(f"  {'':26} {'Baseline':>10} {'Sized':>10}")
    for label, key, fmt in (("Antenna mass [kg]", "antenna", ".2f"), ("TWTA mass [kg]", "twta", ".2f"),
                            ("Transceiver mass [kg]", "transceiver", ".2f"), ("Total mass [kg]", "total", ".2f"),
                            (f"Total + {MASS_MARGIN * 100:.0f}% margin [kg]", "total_margin", ".2f"),
                            ("Transceiver volume [L]", "trans_volume", ".2f"),
                            ("Dish depth [m]", "dish_depth", ".2f"),
                            ("DC power [W]", "dc", ".1f"), ("Heat dissipated [W]", "heat", ".1f")):
        scale = 1e3 if key == "trans_volume" else 1
        print(f"  {label:26} {hw_base[key] * scale:10{fmt}} {hw[key] * scale:10{fmt}}")
    print("=" * 60)

    RESULTS[name] = dict(arch=arch, req=req, D=D_design, P=P_design, D_opt=D_opt,
                         base=base, size=size, hw=hw, hw_base=hw_base, rate=rate)


# =====================================================================
# DESIGN CHECKS
# =====================================================================
def uplink(band_gain, L_pr, rate):
    """X-band telecommand Eb/N0 [dB] at max distance for S/C receive gain band_gain [dBi]."""
    eirp = 10 * np.log10(GS_TX_POWER) + gain(GS_DIAMETER, UPLINK_FREQ) - TX_LOSS
    return (eirp - free_space_loss(D_EARTH_MAX, UPLINK_FREQ) - L_pr - ATMOS_LOSS["X"] - RX_LOSS
            + band_gain - 10 * np.log10(SC_NOISE_TEMP) - BOLTZMANN_DB - 10 * np.log10(rate))


REQ_TC = required_eb_n0("BPSK", "Uncoded")  # dB, uncoded telecommand

for name, r in RESULTS.items():
    band, mod, cod = r["arch"]["band"], r["arch"]["modulation"], r["arch"]["coding"]
    f = DOWNLINK_FREQ[band]
    print()
    print("=" * 60)
    print(f" CHECK - {name.upper()} (sized design)")
    print("=" * 60)
    margin = r["size"]["eb_n0"] - r["req"]
    print(f"  [{ok(margin >= REQ_LINK_MARGIN)}] Downlink margin        {margin:6.2f} dB (min {REQ_LINK_MARGIN:.0f} dB)")
    alpha = beamwidth(r["D"], f)
    print(f"  [{ok(REQ_POINTING <= alpha / 2)}] Pointing in main lobe  {REQ_POINTING:.3f} deg vs alpha/2 = {alpha / 2:.3f} deg")
    print(f"  [{ok(r['D'] <= r['D_opt'])}] Dish <= optimal        {r['D']:.2f} m vs {r['D_opt']:.2f} m")
    print(f"  [{ok(r['D'] <= FAIRING_DIAMETER)}] Dish fits fairing      {r['D']:.2f} m vs {FAIRING_DIAMETER:.2f} m")
    print(f"  [{ok(r['hw']['dc'] <= COMMS_POWER_ALLOC)}] DC power (sized)       {r['hw']['dc']:6.1f} W vs {COMMS_POWER_ALLOC} W allocated")
    print(f"  [{ok(r['hw_base']['dc'] <= COMMS_POWER_ALLOC)}] DC power (baseline)    {r['hw_base']['dc']:6.1f} W vs {COMMS_POWER_ALLOC} W allocated")
    B = bandwidth(r["rate"], mod, cod)
    print(f"  [{ok(B <= BAND_ALLOCATION[band])}] Bandwidth              {B / 1e3:6.1f} kHz vs {BAND_ALLOCATION[band] / 1e6:.0f} MHz allocation")

    G_hga_up = gain(r["D"], UPLINK_FREQ)
    tc_hga = uplink(G_hga_up, pointing_loss(REQ_POINTING, r["D"], UPLINK_FREQ), TC_RATE) - REQ_TC
    print(f"  [{ok(tc_hga >= REQ_LINK_MARGIN)}] Uplink HGA {TC_RATE / 1e3:.0f} kbps      margin {tc_hga:6.2f} dB")
    lga_rate = 10 ** ((uplink(LGA_GAIN, 0.0, 1.0) - REQ_TC - REQ_LINK_MARGIN) / 10)  # bit/s
    print(f"  [info] Safe-mode LGA uplink   max {lga_rate:7.1f} bps at {D_EARTH_MAX / C.AU:.3f} AU")

    # Rate the sized link supports with 3 dB margin, scales with 1/d^2
    for label, d in (("max", D_EARTH_MAX), ("min", D_EARTH_MIN)):
        m = downlink(band, r["D"], r["P"], r["rate"], d=d)["eb_n0"] - r["req"]
        print(f"  [info] Achievable rate at {label} distance ({d / C.AU:.3f} AU): "
              f"{r['rate'] * 10 ** ((m - REQ_LINK_MARGIN) / 10) / 1e3:8.1f} kbps")
    print("=" * 60)


# ---------- Comparison ----------
print()
print("=" * 60)
print(" COMMS COMPARISON (sized designs)")
print("=" * 60)
names = list(RESULTS)
print(f"  {'':24}" + "".join(f"{n:>12}" for n in names))
rows = (
    ("Band",                  lambda r: f"{r['arch']['band']}"),
    ("Modulation",            lambda r: r["arch"]["modulation"]),
    ("Coding",                lambda r: r["arch"]["coding"].split()[0]),
    ("Antenna diameter [m]",  lambda r: f"{r['D']:.2f}"),
    ("RF power [W]",          lambda r: f"{r['P']:.1f}"),
    ("DC power [W]",          lambda r: f"{r['hw']['dc']:.1f}"),
    ("Link margin [dB]",      lambda r: f"{r['size']['eb_n0'] - r['req']:.2f}"),
    ("Beamwidth [deg]",       lambda r: f"{r['size']['alpha_t']:.3f}"),
    ("Mass [kg]",             lambda r: f"{r['hw']['total']:.2f}"),
    ("Mass + margin [kg]",    lambda r: f"{r['hw']['total_margin']:.2f}"),
)
for label, get in rows:
    print(f"  {label:24}" + "".join(f"{get(RESULTS[n]):>12}" for n in names))
print("=" * 60)
