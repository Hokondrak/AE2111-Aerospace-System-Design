###EPS

"""EPS component database transcribed from the supplied component survey.

Units: kg, L, Wh, W, V, A, m², years, and radiation dose in krad(Si)
unless the original survey gave a different or unspecified unit.

Examples (place this file beside the calling Python script)::

    from eps_components import enersys_battery, azur_3g28, airbus_evo_pcdu

    enersys_battery.mass()             # 7.8 kg for ONE ABSL 8S16P module
    2 * enersys_battery.mass()         # 15.6 kg for two modules
    enersys_battery.energy()           # 1628 Wh for ONE module
    azur_3g28.mass(area_m2=1.52)      # 1.3072 kg using the survey's kg/m²
    airbus_evo_pcdu.max_power_W        # 4000 W (at 28 V)

The survey compares *configurations*, not always individual components.
For Ibeos, EnerSys, and MMRTG, per-unit mass/energy/volume/power are
derived by dividing the stated two- or three-unit configuration totals.
Every zero-argument quantity method returns the value for ONE physical unit.
The 160 A and 50 A battery currents were given beside two-battery
configurations; the survey does not say if they are per battery or per pair.
They are preserved as notes, never returned as single-battery ratings.

Solar mass(area_m2) uses the survey's "array specific mass" entry. It is
not a complete deployable-array mass: structure and mechanisms are excluded
or unspecified. No manufacturer specifications have been independently
verified. Unknown values are left unknown instead of estimated.

Source: supplied EPS chapter, "Component Survey and Down-Selection" tables.
Each component also carries its original LaTeX bibliography citation key.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isfinite
from typing import Union


class MissingSpecificationError(ValueError):
    """A requested figure was absent from the supplied component table."""


@dataclass(frozen=True)
class Battery:
    key: str
    manufacturer: str
    model: str
    citation_key: str
    energy_Wh: float
    mass_kg: float
    volume_L: float
    operating_voltage_V: tuple[float, float]
    discharge_current_per_battery_A: float | None
    source_configuration: str
    cycle_life_cycles: int | None = None
    cycle_life_dod: float | None = None
    approximate_mass_and_volume: bool = False
    selected_for_architecture_1: bool = False
    note: str = ""

    def mass(self) -> float:
        """Mass of ONE battery in kg."""
        return self.mass_kg

    def energy(self) -> float:
        """Nameplate energy of ONE battery in Wh, not usable EOL energy."""
        return self.energy_Wh

    def volume(self) -> float:
        """Volume of ONE battery in L."""
        return self.volume_L

    def discharge_current(self) -> float:
        """Single-battery current in A; raise if the table is ambiguous."""
        if self.discharge_current_per_battery_A is None:
            raise MissingSpecificationError(
                f"Single-battery discharge current for {self.model} is not "
                f"established by the supplied table. {self.source_configuration}"
            )
        return self.discharge_current_per_battery_A


@dataclass(frozen=True)
class SolarCellTechnology:
    key: str
    manufacturer: str
    model: str
    citation_key: str
    eol_efficiency: float
    array_specific_mass_kg_m2: float
    mercury_heritage: str
    hiht_suitability: str
    selected_for_architecture_1: bool = False
    note: str = ""

    def mass(self, area_m2: float) -> float:
        """Survey-specific area mass in kg; NOT a final array assembly mass."""
        if isinstance(area_m2, bool) or not isinstance(area_m2, (int, float)):
            raise ValueError("area_m2 must be a finite, nonnegative number")
        if not isfinite(area_m2) or area_m2 < 0:
            raise ValueError("area_m2 must be a finite, nonnegative number")
        return self.array_specific_mass_kg_m2 * area_m2


@dataclass(frozen=True)
class RTG:
    key: str
    model: str
    citation_key: str
    launch_power_W: float
    mass_kg: float
    source_configuration: str
    dimensions: str
    operating_environment: str
    heritage: str
    selected_for_architecture_2: bool = False
    note: str = ""

    def mass(self) -> float:
        """Mass of ONE generator in kg."""
        return self.mass_kg

    def power_at_launch(self) -> float:
        """Electrical power of ONE generator in W at launch."""
        return self.launch_power_W

    def specific_power_at_launch(self) -> float:
        """W/kg, computed from the stated power and mass."""
        return self.launch_power_W / self.mass_kg


@dataclass(frozen=True)
class PCDU:
    key: str
    manufacturer: str
    model: str
    citation_key: str
    max_power_W: float
    min_power_W: float | None
    power_condition: str
    main_bus: str
    solar_regulation: str
    mppt_efficiency: str
    battery_capability: str
    radiation_capability: str
    design_life: str
    selected_for_architecture_1: bool = False
    note: str = ""

    def mass(self) -> float:
        """Raise until a configuration-specific PCDU mass is provided."""
        raise MissingSpecificationError(
            f"Mass of {self.model} is not specified in the supplied survey."
        )


# The Saft row is one VES16 8S16P battery assembly. The other rows are pairs:
# nameplate energy, mass, and volume are divided by two for each battery.
ibeos_battery = Battery(
    key="ibeos_b28_1100", manufacturer="Ibeos", model="B28-1100",
    citation_key="ibeos_b28_1100", energy_Wh=1100.0, mass_kg=7.8,
    volume_L=6.15, operating_voltage_V=(24.0, 33.6),
    discharge_current_per_battery_A=None,
    source_configuration="Table: two batteries, 2200 Wh, 15.6 kg, "
                         "12.30 L, 160 A current rating (basis unspecified).",
    selected_for_architecture_1=True,
    note="Cycle-life evidence: supplier data required.",
)

enersys_battery = Battery(
    key="enersys_absl_8s16p", manufacturer="EnerSys", model="ABSL 8S16P",
    citation_key="enersys_absl_8s16p_2026", energy_Wh=1628.0, mass_kg=7.8,
    volume_L=7.24, operating_voltage_V=(24.0, 33.6),
    discharge_current_per_battery_A=None,
    source_configuration="Table: two batteries, 3256 Wh, 15.6 kg, "
                         "14.48 L, 50 A current rating (basis unspecified).",
    note="Cycle-life evidence: supplier data required. One 1628 Wh module "
         "exceeds the chapter's 1367.8 Wh Architecture 2 nameplate requirement.",
)

saft_battery = Battery(
    key="saft_ves16_8s16p", manufacturer="Saft", model="VES16 8S16P",
    citation_key="NASA_SST_SOA_TCS_2023", energy_Wh=2048.0, mass_kg=22.5,
    volume_L=18.8, operating_voltage_V=(26.4, 32.8),
    discharge_current_per_battery_A=72.0,
    source_configuration="Table: one VES16 8S16P battery.",
    cycle_life_cycles=7500, cycle_life_dod=0.30,
    approximate_mass_and_volume=True,
)

# These coefficients are taken from the solar comparison table, not the
# separate first-level sizing model (which used 2 kg/m² for the array).
azur_3g28 = SolarCellTechnology(
    key="azur_modified_3g28", manufacturer="AZUR SPACE",
    model="Modified 3G28", citation_key="azur_3g28c_2012",
    eol_efficiency=0.28, array_specific_mass_kg_m2=0.86,
    mercury_heritage="BepiColombo", hiht_suitability="Demonstrated",
    selected_for_architecture_1=True,
    note="Complete panel structure and deployment hardware remain mission-specific.",
)

azur_4g32 = SolarCellTechnology(
    key="azur_4g32_advanced", manufacturer="AZUR SPACE",
    model="4G32 Advanced", citation_key="azur_4g32_2025",
    eol_efficiency=0.32, array_specific_mass_kg_m2=1.75,
    mercury_heritage="No equivalent Mercury heritage identified",
    hiht_suitability="Not demonstrated for this mission environment",
)

# The MMRTG row gives three units; values below are divided by three.
# Neither table supplies a decay law, so only launch power is provided.
mmrtg = RTG(
    key="mmrtg", model="MMRTG", citation_key="nasa_mmrtg_2020",
    launch_power_W=110.0, mass_kg=45.0,
    source_configuration="Table: three MMRTGs, 330 W, 135 kg.",
    dimensions="Per unit: approximately 64 cm × 66 cm",
    operating_environment="Vacuum or planetary atmosphere",
    heritage="Long-duration NASA qualification",
)

gphs_rtg = RTG(
    key="gphs_rtg", model="GPHS-RTG", citation_key="cataldo2011radioisotope",
    launch_power_W=300.0, mass_kg=55.9,
    source_configuration="Table: one GPHS-RTG, 300 W, 55.9 kg.",
    dimensions="42.2 cm diameter × 114 cm",
    operating_environment="Vacuum", heritage="Galileo flight heritage",
    selected_for_architecture_2=True,
    note="The chapter's parametric RTG mass (107.61 kg) differs from this "
         "surveyed hardware mass (55.9 kg); do not interchange them.",
)

bradford_pcdu = PCDU(
    key="bradford_supernova", manufacturer="Bradford", model="SuperNova",
    citation_key="bradford_supernova_2024", min_power_W=300.0,
    max_power_W=1500.0, power_condition="Surveyed range: 300–1500 W",
    main_bus="Approximately 28 V", solar_regulation="MPPT; DET optional",
    mppt_efficiency="95%", battery_capability="50 A charge/discharge",
    radiation_capability=">30 krad (unit not specified in table)",
    design_life=">5 years",
)

starbuck_mini_pcdu = PCDU(
    key="aacclyde_starbuck_mini", manufacturer="AAC Clyde Space",
    model="STARBUCK-MINI", citation_key="aacclyde_starbuckmini_2026",
    min_power_W=None, max_power_W=2500.0,
    power_condition="Up to 2.5 kW", main_bus="22–34 V",
    solar_regulation="MPPT or S3R",
    mppt_efficiency="Configuration dependent",
    battery_capability="CC-CV charging",
    radiation_capability="20 krad; qualified >30 krad(Si)",
    design_life="5–7 years",
)

airbus_evo_pcdu = PCDU(
    key="airbus_evo", manufacturer="Airbus", model="EVO PCDU",
    citation_key="airbus_evo_pcdu_2021", min_power_W=None,
    max_power_W=4000.0, power_condition="Up to 4 kW at 28 V",
    main_bus="28 / 50 / 100 V", solar_regulation="MPPT or DET/S3R",
    mppt_efficiency=">95%", battery_capability="Up to 130 A",
    radiation_capability="Interplanetary compatible",
    design_life="15 years", selected_for_architecture_1=True,
    note="Final PCDU mass depends on configuration and is not given in the chapter.",
)


Component = Union[Battery, SolarCellTechnology, RTG, PCDU]

COMPONENTS: dict[str, Component] = {
    component.key: component for component in (
        ibeos_battery, enersys_battery, saft_battery,
        azur_3g28, azur_4g32, mmrtg, gphs_rtg,
        bradford_pcdu, starbuck_mini_pcdu, airbus_evo_pcdu,
    )
}


def get_component(key: str) -> Component:
    """Look up a component by its stable catalog key (KeyError if absent)."""
    return COMPONENTS[key]


def component_data(key: str) -> dict:
    """Return all recorded specifications as a plain, editable dictionary."""
    return asdict(get_component(key))


__all__ = [
    "Battery", "SolarCellTechnology", "RTG", "PCDU",
    "MissingSpecificationError", "COMPONENTS", "get_component",
    "component_data", "ibeos_battery", "enersys_battery", "saft_battery",
    "azur_3g28", "azur_4g32", "mmrtg", "gphs_rtg",
    "bradford_pcdu", "starbuck_mini_pcdu", "airbus_evo_pcdu",
]
