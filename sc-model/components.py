"""
Component database, from the EPS chapter "Component Survey and Down-Selection" tables.

One dictionary per component type, keyed by a short name. Every number is for ONE
physical unit; None = not given in the survey. Units: kg, L, Wh, W, V, A, m².
"ref" is the LaTeX bibliography key.

    import components as COMP
    bat = COMP.BATTERIES["ibeos"]
    2 * bat["mass"]                                   # kg, two batteries
    COMP.SOLAR_CELLS["azur_3g28"]["areal_mass"] * 1.52  # kg, cells only

Where the survey compares a configuration (two batteries, three MMRTGs) the totals are
divided by the number of units. Solar "areal_mass" is the survey's array specific mass,
NOT a full deployable array (structure and mechanisms excluded or unspecified).
No manufacturer data has been verified independently.
"""

# ---------- Batteries ----------
# Ibeos and EnerSys rows are pairs: energy, mass and volume divided by two.
# The 160 A / 50 A currents were given next to the pair, per battery or per pair is
# not stated, so "current" is None and the value is kept in the note.
BATTERIES = {
    "ibeos": dict(  # selected: Architecture 1
        manufacturer="Ibeos", model="B28-1100", ref="ibeos_b28_1100",
        energy=1100.0,          # Wh, nameplate (not usable EOL energy)
        mass=7.8,               # kg
        volume=6.15,            # L
        voltage=(24.0, 33.6),   # V, operating range
        current=None,           # A, max discharge
        cycle_life=None,        # (cycles, DoD)
        note="Table: two batteries, 2200 Wh, 15.6 kg, 12.30 L, 160 A (basis unspecified). "
             "Cycle life: supplier data required.",
    ),
    "enersys": dict(  # selected: Architecture 2
        manufacturer="EnerSys", model="ABSL 8S16P", ref="enersys_absl_8s16p_2026",
        energy=1628.0, mass=7.8, volume=7.24, voltage=(24.0, 33.6),
        current=None, cycle_life=None,
        note="Table: two batteries, 3256 Wh, 15.6 kg, 14.48 L, 50 A (basis unspecified). "
             "Cycle life: supplier data required.",
    ),
    "saft": dict(
        manufacturer="Saft", model="VES16 8S16P", ref="NASA_SST_SOA_TCS_2023",
        energy=2048.0, mass=22.5, volume=18.8, voltage=(26.4, 32.8),
        current=72.0, cycle_life=(7500, 0.30),
        note="Table: one battery. Mass and volume approximate.",
    ),
}

# ---------- Solar cells ----------
# From the solar comparison table, not the first-level sizing (2 kg/m² in eps.py).
SOLAR_CELLS = {
    "azur_3g28": dict(  # selected: Architecture 1 and 2
        manufacturer="AZUR SPACE", model="Modified 3G28", ref="azur_3g28c_2012",
        efficiency=0.28,        # -, EOL
        areal_mass=0.86,        # kg/m²
        heritage="BepiColombo", hiht="Demonstrated",
        note="Panel structure and deployment hardware are mission-specific.",
    ),
    "azur_4g32": dict(
        manufacturer="AZUR SPACE", model="4G32 Advanced", ref="azur_4g32_2025",
        efficiency=0.32, areal_mass=1.75,
        heritage="No equivalent Mercury heritage identified",
        hiht="Not demonstrated for this mission environment",
        note="",
    ),
}

# ---------- RTGs ----------
# Power at launch only; the survey gives no decay law.
RTGS = {
    "mmrtg": dict(
        model="MMRTG", ref="nasa_mmrtg_2020",
        power=110.0,            # W, at launch
        mass=45.0,              # kg
        dimensions="approx. 64 cm × 66 cm",
        environment="Vacuum or planetary atmosphere",
        heritage="Long-duration NASA qualification",
        note="Table: three MMRTGs, 330 W, 135 kg.",
    ),
    "gphs_rtg": dict(  # selected: Architecture 2
        model="GPHS-RTG", ref="cataldo2011radioisotope",
        power=300.0, mass=55.9,
        dimensions="42.2 cm diameter × 114 cm",
        environment="Vacuum", heritage="Galileo",
        note="The chapter's parametric RTG mass (107.61 kg) differs from this hardware mass.",
    ),
}

# ---------- PCDUs ----------
# No PCDU mass is given; it depends on the configuration.
PCDUS = {
    "bradford": dict(
        manufacturer="Bradford", model="SuperNova", ref="bradford_supernova_2024",
        power=(300.0, 1500.0),  # W, (min, max) handled
        mass=None,              # kg
        bus="approx. 28 V", regulation="MPPT; DET optional", mppt_efficiency="95%",
        battery="50 A charge/discharge",
        radiation=">30 krad (unit not specified)", life=">5 years",
    ),
    "starbuck_mini": dict(
        manufacturer="AAC Clyde Space", model="STARBUCK-MINI", ref="aacclyde_starbuckmini_2026",
        power=(None, 2500.0), mass=None,
        bus="22-34 V", regulation="MPPT or S3R", mppt_efficiency="Configuration dependent",
        battery="CC-CV charging",
        radiation="20 krad; qualified >30 krad(Si)", life="5-7 years",
    ),
    "airbus_evo": dict(  # selected: Architecture 1 and 2
        manufacturer="Airbus", model="EVO PCDU", ref="airbus_evo_pcdu_2021",
        power=(None, 4000.0),   # W, at 28 V
        mass=None,
        bus="28 / 50 / 100 V", regulation="MPPT or DET/S3R", mppt_efficiency=">95%",
        battery="Up to 130 A",
        radiation="Interplanetary compatible", life="15 years",
    ),
}
