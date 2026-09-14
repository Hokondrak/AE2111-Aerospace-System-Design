from src.case_parser import CaseParser
import src.constants as ct
import math
import os

# Function to list available case files
def list_case_files(directory='cases'):
    return sorted([f for f in os.listdir(directory) if f.startswith('case') and f.endswith('.txt')])

# Text-based UI for case selection
def select_case():
    cases = list_case_files()
    if not cases:
        print("No case files found in 'cases/' directory.")
        exit(1)
    
    while True:
        print("\n<===> Available cases <===>\n")
        for i, case in enumerate(cases, 1):
            print(f"{i}. {case}")
        print('\n<==========================>')
        print("\nEnter the number of the case to select (or '0' to quit):")
        
        user_input = input().strip().lower()
        if user_input == '0':
            print("Exiting.")
            exit(0)
        
        try:
            selection = int(user_input)
            if 1 <= selection <= len(cases):
                return os.path.join('cases', cases[selection - 1])
            else:
                print(f"Invalid selection. Please choose a number between 1 and {len(cases)}.")
        except ValueError:
            print("Invalid input. Please enter a number or '0' to quit.")

# Main execution
case_file = select_case()

# Create a parser instance
parser = CaseParser()
# Parse the selected case file
case_data = parser.parse_case_file(case_file)

print(f"\nAnalyzing {case_file}...")
print(f"Satellite in {case_data['planet']} orbit.\n")

# ============================================================================
# EXTRACT PARAMETERS
# ============================================================================
planet = case_data['planet']
tx_power_spacecraft = case_data['tx_power_spacecraft']
tx_power_ground = case_data['tx_power_ground']
tx_loss_factor = case_data['tx_loss_factor']
rx_loss_factor = case_data['rx_loss_factor']
antenna_diameter_spacecraft = case_data['antenna_diameter_spacecraft']
antenna_diameter_ground = case_data['antenna_diameter_ground']
downlink_frequency = case_data['downlink_frequency']
turn_around_ratio = case_data['turn_around_ratio']
modulation_type = case_data['modulation_type']
height_m = case_data['orbit_altitude']  # Already converted to meters by parser
offset_deg = case_data['pointing_offset_angle_spacecraft']
swath_angle_deg = case_data['payload_swath_width_angle']
bits_per_pixel = case_data['payload_bits_per_pixel']
pixel_size_deg = case_data['payload_pixel_size']  # Already converted to degrees by parser
duty_cycle = case_data['payload_duty_cycle']  # Already converted to fraction by parser
required_uplink_data_rate = case_data['required_uplink_data_rate']
required_ber = case_data['required_ber']
elongation_angle = case_data.get('elongation_angle', 0)
downlink_time_fraction = case_data['payload_downlink_time']  # Already converted to fraction of day

# ============================================================================
# FREQUENCY AND WAVELENGTH CALCULATIONS
# ============================================================================
uplink_frequency = downlink_frequency * turn_around_ratio
lambda_down = ct.SPEED_OF_LIGHT / downlink_frequency
lambda_up = ct.SPEED_OF_LIGHT / uplink_frequency

# ============================================================================
# ANTENNA GAIN CALCULATIONS
# ============================================================================
def calculate_gain(diameter, wavelength):

    G_lin = ct.DEFAULT_ANTENNA_EFFICIENCY * (math.pi * diameter / wavelength) ** 2
    G_db = 10 * math.log10(G_lin)
    return G_lin, G_db

# Transmitter gainzzzzzzzzzzzzzzzzzzzzzzz
trans_gain_up_lin, trans_gain_up_db = calculate_gain(antenna_diameter_ground, lambda_up)
trans_gain_down_lin, trans_gain_down_db = calculate_gain(antenna_diameter_spacecraft, lambda_down)

# Receiver gainzzzzzzzzz
receiv_gain_up_lin, receiv_gain_up_db = calculate_gain(antenna_diameter_spacecraft, lambda_up)
receiv_gain_down_lin, receiv_gain_down_db = calculate_gain(antenna_diameter_ground, lambda_down)

# ============================================================================
# DISTANCE CALCULATION (SLANT RANGE)
# ============================================================================
def calculate_distance(planet, height_m):

    if planet == 'Earth':
        # Use 5 degree elevation angle
        elevation_angle = 5
        R_earth = ct.EARTH_RADIUS_KM * 1000  # Convert to meters
        distance = math.sqrt(
            (R_earth + height_m)**2 - 
            (R_earth * math.cos(math.radians(elevation_angle)))**2
        ) - R_earth * math.sin(math.radians(elevation_angle))
    elif planet == 'Moon':
        distance = ct.PLANETS['Moon']
    else:
        # For other planets, use elongation angle
        distance = math.sqrt(
            ct.PLANETS[planet]**2 + ct.PLANETS["Earth"]**2 - 
            2 * ct.PLANETS[planet] * ct.PLANETS["Earth"] * math.cos(math.radians(elongation_angle))
        )
    return distance

distance_m = calculate_distance(planet, height_m)

# ============================================================================
# FREE SPACE PATH LOSS (FSPL)
# ============================================================================
def calculate_FSPL(distance, wavelength):

    FSPL_lin = (4 * math.pi * distance / wavelength) ** 2
    FSPL_db = 10 * math.log10(FSPL_lin)
    return FSPL_lin, FSPL_db

FSPL_up_lin, FSPL_up_db = calculate_FSPL(distance_m, lambda_up)
FSPL_down_lin, FSPL_down_db = calculate_FSPL(distance_m, lambda_down)

# ============================================================================
# POINTING LOSS
# ============================================================================
def calculate_pointing_loss(diameter, wavelength, offset_deg):

    theta_3db = 70 * (wavelength / diameter)  # 3dB beamwidth in degrees
    point_loss_db = 12 * (offset_deg / theta_3db) ** 2
    return point_loss_db

point_loss_down = calculate_pointing_loss(antenna_diameter_spacecraft, lambda_down, offset_deg)
point_loss_up = calculate_pointing_loss(antenna_diameter_spacecraft, lambda_up, offset_deg)

# Apply pointing loss to spacecraft antenna (both transmit on downlink and receive on uplink)
trans_gain_down_db -= point_loss_down
receiv_gain_up_db -= point_loss_up

# ============================================================================
# EIRP (EQUIVALENT ISOTROPIC RADIATED POWER)
# ============================================================================
def calculate_EIRP(tx_power, loss_factor, gain_db):

    tx_power_db = 10 * math.log10(tx_power)
    loss_db = -10 * math.log10(loss_factor)  # Convert loss factor to dB (negative)
    return tx_power_db + gain_db - loss_db

EIRP_down_db = calculate_EIRP(tx_power_spacecraft, tx_loss_factor, trans_gain_down_db)
EIRP_up_db = calculate_EIRP(tx_power_ground, tx_loss_factor, trans_gain_up_db)

# ============================================================================
# PAYLOAD DATA RATE CALCULATION 
# ============================================================================
# Calculate orbital velocity
orbital_velocity = math.sqrt(ct.G * ct.PLANET_WEIGHTS[planet] / (height_m + ct.PLANET_RADII[planet]))

# Convert angular measurements to linear dimensions
# Swath width at nadir (ground level)
swath_width_m = 2 * height_m * math.tan(math.radians(swath_angle_deg) / 2)

# Pixel size at nadir (ground level)
pixel_size_rad = math.radians(pixel_size_deg)
pixel_size_m = height_m * pixel_size_rad

# Payload data generation rate 
# RG = BP * (SW * V) / PS^2
data_rate_payload = bits_per_pixel * (swath_width_m * orbital_velocity) / (pixel_size_m ** 2)

# Required downlink data rate
# R = RG * (DC / TDL)
required_downlink_rate = data_rate_payload * (duty_cycle / downlink_time_fraction)

print(f"=== PAYLOAD ANALYSIS ===")
print(f"Orbital velocity: {orbital_velocity:.2f} m/s")
print(f"Swath width: {swath_width_m/1000:.2f} km")
print(f"Pixel size: {pixel_size_m:.2f} m")
print(f"Payload data generation rate: {data_rate_payload/1e9} Gbps")
print(f"Duty cycle: {duty_cycle*100:.0f}%")
print(f"Downlink time: {downlink_time_fraction*24:.2f} hours/day")
print(f"Required downlink rate: {required_downlink_rate/1e9} Gbps\n")

# ============================================================================
# LINK BUDGET ANALYSIS - DOWNLINK 
# ============================================================================
# Calculate G/T (Figure of Merit)
G_over_T_down_db = receiv_gain_down_db - 10 * math.log10(ct.SYSTEM_NOISE_TEMP)

# Convert loss factors to dB losses
rx_loss_db = -10 * math.log10(rx_loss_factor)

# Eb/N0 = EIRP - FSPL - Losses + G/T - kB - Rb
bit_rate_down_db = 10 * math.log10(required_downlink_rate)

eb_n0_received_down_db = (
    EIRP_down_db 
    - FSPL_down_db 
    + G_over_T_down_db 
    - ct.BOLTZMANN_CONSTANT_DB  # Note: this is -228.6, so subtracting adds it
    - bit_rate_down_db
    - rx_loss_db
)

# Determine required Eb/N0 based on modulation and BER
# For uncoded BPSK at BER=10^-6, required Eb/N0 == 10.5 dB
required_eb_n0_db = 10.5

# Calculate link margin
margin_down_db = eb_n0_received_down_db - required_eb_n0_db

# ============================================================================
# LINK BUDGET ANALYSIS - UPLINK
# ============================================================================
G_over_T_up_db = receiv_gain_up_db - 10 * math.log10(ct.SYSTEM_NOISE_TEMP)
bit_rate_up_db = 10 * math.log10(required_uplink_data_rate)

eb_n0_received_up_db = (
    EIRP_up_db 
    - FSPL_up_db 
    + G_over_T_up_db 
    - ct.BOLTZMANN_CONSTANT_DB
    - bit_rate_up_db
    - rx_loss_db
)

margin_up_db = eb_n0_received_up_db - required_eb_n0_db

# ============================================================================
# RESULTS OUTPUT
# ============================================================================
print(f"=== LINK BUDGET RESULTS ===\n")

# Downlink
pass_d = margin_down_db >= 3.0  
status_d = "PASS ✅" if pass_d else "FAIL ❌"
print(f"===> DOWNLINK = {status_d} <===")
print(f"EIRP: {EIRP_down_db:.2f} dBW")
print(f"Free Space Path Loss: {FSPL_down_db:.2f} dB")
print(f"G/T: {G_over_T_down_db:.2f} dB/K")
print(f"Required data rate: {required_downlink_rate/1e9} Gbps")
print(f"Received Eb/N0: {eb_n0_received_down_db:.2f} dB")
print(f"Required Eb/N0: {required_eb_n0_db:.2f} dB")
print(f"Link Margin: {margin_down_db:.2f} dB")
if not pass_d:
    print(f"⚠️  Need {3.0 - margin_down_db:.2f} dB more margin to pass")
print()

# Uplink
pass_u = margin_up_db >= 3.0
status_u = "PASS ✅" if pass_u else "FAIL ❌"
print(f"===> UPLINK = {status_u} <===")
print(f"EIRP: {EIRP_up_db:.2f} dBW")
print(f"Free Space Path Loss: {FSPL_up_db:.2f} dB")
print(f"G/T: {G_over_T_up_db:.2f} dB/K")
print(f"Required data rate: {required_uplink_data_rate/1e6:.2f} Mbps")
print(f"Received Eb/N0: {eb_n0_received_up_db:.2f} dB")
print(f"Required Eb/N0: {required_eb_n0_db:.2f} dB")
print(f"Link Margin: {margin_up_db:.2f} dB")
if not pass_u:
    print(f"⚠️  Need {3.0 - margin_up_db:.2f} dB more margin to pass")
print()

# Debug information
# print(f"=== DEBUG INFO ===")
# print(f"Distance: {distance_m/1000:.1f} km")
# print(f"Downlink frequency: {downlink_frequency/1e9:.2f} GHz")
# print(f"Uplink frequency: {uplink_frequency/1e9:.2f} GHz")
# print(f"System noise temperature: {ct.SYSTEM_NOISE_TEMP} K")
# print(f"Boltzmann constant: {ct.BOLTZMANN_CONSTANT_DB} dB(J/K)")


# ============================================================================

print(f"\n{'='*60}")
print(f"===== ADDITIONAL INFO - DETAILED LINK BUDGET =====")
print(f"{'='*60}\n")

# Convert all parameters to dB
tx_power_spacecraft_db = 10 * math.log10(tx_power_spacecraft)
tx_power_ground_db = 10 * math.log10(tx_power_ground)
tx_loss_db = -10 * math.log10(tx_loss_factor)
rx_loss_db = -10 * math.log10(rx_loss_factor)
bit_rate_down_db = 10 * math.log10(required_downlink_rate)
bit_rate_up_db = 10 * math.log10(required_uplink_data_rate)

print(f"===> DOWNLINK BUDGET (All quantities in dB) <===")
print(f"{'-'*60}")
print(f"Transmitter (Spacecraft):")
print(f"  Transmitter Power:              {tx_power_spacecraft_db:>10.2f} dBW")
print(f"  Antenna Gain (with pointing):   {trans_gain_down_db:>10.2f} dB")
print(f"  Pointing Loss:                  {-point_loss_down:>10.2f} dB")
print(f"  Transmitter Losses:             {tx_loss_db:>10.2f} dB")
print(f"  EIRP:                           {EIRP_down_db:>10.2f} dBW")
print(f"\nPath:")
print(f"  Distance:                       {distance_m/1000:>10.1f} km")
print(f"  Frequency:                      {downlink_frequency/1e9:>10.2f} GHz")
print(f"  Wavelength:                     {lambda_down*1000:>10.2f} mm")
print(f"  Free Space Path Loss:           {-FSPL_down_db:>10.2f} dB")
print(f"\nReceiver (Ground Station):")
print(f"  Antenna Gain:                   {receiv_gain_down_db:>10.2f} dB")
print(f"  System Noise Temperature:       {ct.SYSTEM_NOISE_TEMP:>10.0f} K")
print(f"  G/T:                            {G_over_T_down_db:>10.2f} dB/K")
print(f"  Receiver Losses:                {rx_loss_db:>10.2f} dB")
print(f"\nData Rate & Performance:")
print(f"  Required Bit Rate:              {bit_rate_down_db:>10.2f} dB(Hz)")
print(f"                                  {required_downlink_rate/1e6:>10.2f} Mbps")
print(f"  Boltzmann Constant k:           {ct.BOLTZMANN_CONSTANT_DB:>10.1f} dB(J/K)")
print(f"  Received Eb/N0:                 {eb_n0_received_down_db:>10.2f} dB")
print(f"  Required Eb/N0:                 {required_eb_n0_db:>10.2f} dB")
print(f"  Link Margin:                    {margin_down_db:>10.2f} dB")

print(f"\n{'='*60}")
print(f"===> UPLINK BUDGET (All quantities in dB) <===")
print(f"{'-'*60}")
print(f"Transmitter (Ground Station):")
print(f"  Transmitter Power:              {tx_power_ground_db:>10.2f} dBW")
print(f"  Antenna Gain:                   {trans_gain_up_db:>10.2f} dB")
print(f"  Transmitter Losses:             {tx_loss_db:>10.2f} dB")
print(f"  EIRP:                           {EIRP_up_db:>10.2f} dBW")
print(f"\nPath:")
print(f"  Distance:                       {distance_m/1000:>10.1f} km")
print(f"  Frequency:                      {uplink_frequency/1e9:>10.2f} GHz")
print(f"  Wavelength:                     {lambda_up*1000:>10.2f} mm")
print(f"  Free Space Path Loss:           {-FSPL_up_db:>10.2f} dB")
print(f"\nReceiver (Spacecraft):")
print(f"  Antenna Gain (with pointing):   {receiv_gain_up_db:>10.2f} dB")
print(f"  Pointing Loss:                  {-point_loss_up:>10.2f} dB")
print(f"  System Noise Temperature:       {ct.SYSTEM_NOISE_TEMP:>10.0f} K")
print(f"  G/T:                            {G_over_T_up_db:>10.2f} dB/K")
print(f"  Receiver Losses:                {rx_loss_db:>10.2f} dB")
print(f"\nData Rate & Performance:")
print(f"  Required Bit Rate:              {bit_rate_up_db:>10.2f} dB(Hz)")
print(f"                                  {required_uplink_data_rate/1e6:>10.2f} Mbps")
print(f"  Boltzmann Constant k:           {ct.BOLTZMANN_CONSTANT_DB:>10.1f} dB(J/K)")
print(f"  Received Eb/N0:                 {eb_n0_received_up_db:>10.2f} dB")
print(f"  Required Eb/N0:                 {required_eb_n0_db:>10.2f} dB")
print(f"  Link Margin:                    {margin_up_db:>10.2f} dB")
print(f"{'='*60}\n")