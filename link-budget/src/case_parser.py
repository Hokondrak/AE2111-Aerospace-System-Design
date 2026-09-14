import re
from typing import Dict, Any

class CaseParser:
    def __init__(self):
        # Conversion factors
        self.unit_conversions = {
            'W': 1,
            'GHz': 1e9,
            'MHz': 1e6,
            'km': 1000,
            'deg': 1,
            'arcmin': 1/60,    # convert to degrees
            'bit/s': 1,
            'm': 1,
            'hr': 1,           # hours
            'day': 24,         # convert days to hours
            'hr/day': 1/24,    # fraction of day
            '%': 0.01,
            '-': 1
        }

    def parse_case_file(self, filepath: str) -> Dict[str, Any]:
        """Parse a case file and return parameter dictionary"""
        params = {}

        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
        except Exception as e:
            raise

        parsed_count = 0
        skipped_count = 0

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                skipped_count += 1
                continue

            # Parameter with unit
            match = re.match(r'^(.+?)\s*\[(.+?)\]\s*:\s*(.+)$', line)
            if match:
                param_name = match.group(1).strip()
                unit = match.group(2).strip()
                value_str = match.group(3).strip()

                value = self._parse_value(value_str, unit)
                key = self._param_name_to_key(param_name)
                params[key] = value
                parsed_count += 1
            else:
                # Planet line without unit
                planet_match = re.match(r'^Planet:\s*(.+)$', line)
                if planet_match:
                    params['planet'] = planet_match.group(1).strip()
                    parsed_count += 1

        return params

    def _parse_value(self, value_str: str, unit: str) -> float:
        """Parse numeric value with unit handling"""
        value_str = value_str.strip()

        if value_str.upper() == 'NA':
            return 0.0

        # Convert fractions like "221/240"
        if '/' in value_str and not any(c.isalpha() for c in value_str):
            try:
                numerator, denominator = value_str.split('/')
                value = float(numerator) / float(denominator)
            except ValueError:
                value = float(value_str.split()[0])
        else:
            # Extract number before any embedded unit
            num_match = re.match(r'([\d.eE\+\-]+)', value_str)
            if num_match:
                value = float(num_match.group(1))
            else:
                # Fallback: return as string
                return value_str

        # Handle percentages
        if '%' in value_str:
            value *= 0.01

        # Handle embedded units like "hr/day"
        embedded_unit_match = re.search(r'([a-zA-Z/]+)', value_str.replace(unit, '').strip())
        if embedded_unit_match:
            embedded_unit = embedded_unit_match.group(1)
            if embedded_unit in self.unit_conversions:
                value *= self.unit_conversions[embedded_unit]
            elif '/' in embedded_unit:
                parts = embedded_unit.split('/')
                if len(parts) == 2:
                    base, div = parts
                    if base in self.unit_conversions and div in self.unit_conversions:
                        value *= self.unit_conversions[base] / self.unit_conversions[div]

        # Apply main unit conversion
        if unit in self.unit_conversions:
            value *= self.unit_conversions[unit]

        return value

    def _param_name_to_key(self, param_name: str) -> str:
        """Convert parameter name to snake_case"""
        key = re.sub(r'[\s\(\)/]+', '_', param_name.lower()).strip('_')
        # Handle specific mappings
        replacements = {
            'loss_factor_transmitter': 'tx_loss_factor',
            'loss_factor_receiver': 'rx_loss_factor',
            'transmitter_power_spacecraft': 'tx_power_spacecraft',
            'transmitter_power_ground_station': 'tx_power_ground',
            'antenna_diameter_spacecraft_parabolic_antenna': 'antenna_diameter_spacecraft',
            'antenna_diameter_ground_station_parabolic_antenna': 'antenna_diameter_ground',
            'turn_around_ratio_uplink_downlink_frequency': 'turn_around_ratio',
            'elongation_angle_angle_between_spacecraft-sun_line_and_earth-sun_line': 'elongation_angle',
            'modulation_coding_type': 'modulation_type'
        }
        return replacements.get(key, key)


if __name__ == "__main__":
    parser = CaseParser()
    print("CaseParser module loaded successfully")
