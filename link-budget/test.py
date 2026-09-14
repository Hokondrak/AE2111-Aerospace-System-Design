import numpy as np
import matplotlib.pyplot as plt

# Data for clean and flapped wings
clean_alpha_0 = -3.2  # Zero-lift angle (deg)
clean_cl_max = 1.1932  # Max lift coefficient
clean_alpha_max = 10.63  # Angle at CL_max (deg)

flapped_alpha_0 = -11.75  # Zero-lift angle (deg)
flapped_cl_max = 2.19  # Max lift coefficient
flapped_alpha_max = 2.05  # Angle at CL_max (deg)

# Calculate lift curve slopes
clean_slope = clean_cl_max / (clean_alpha_max - clean_alpha_0)  # ~0.0863 per deg
flapped_slope = flapped_cl_max / (flapped_alpha_max - flapped_alpha_0)  # ~0.1510 per deg

# Fitted parameters for Kirchhoff stall model
clean_a1 = 8  # For 0.25 deg transition width
clean_alpha_star = clean_alpha_max + 0.25  # Adjusted for transition at max

flapped_a1 = 8  # For 0.25 deg transition width
flapped_alpha_star = flapped_alpha_max + 0.25  # Adjusted for transition at max

# Function to compute CL using Kirchhoff model
def compute_cl(alpha, alpha_0, slope, a1, alpha_star):
    f = 0.5 * (1 - np.tanh(a1 * (alpha - alpha_star)))
    multiplier = (1 + np.sqrt(f))**2 / 4.0
    return slope * (alpha - alpha_0) * multiplier

# Generate alpha ranges for each curve
alpha_clean = np.linspace(clean_alpha_0, clean_alpha_max + 0.25, 250)
alpha_flapped = np.linspace(flapped_alpha_0, flapped_alpha_max + 0.25, 250)

# Compute CL for each
clean_cl = compute_cl(alpha_clean, clean_alpha_0, clean_slope, clean_a1, clean_alpha_star)
flapped_cl = compute_cl(alpha_flapped, flapped_alpha_0, flapped_slope, flapped_a1, flapped_alpha_star)

# Verify CL_max values at alpha_max
clean_cl_at_max = compute_cl(clean_alpha_max, clean_alpha_0, clean_slope, clean_a1, clean_alpha_star)
flapped_cl_at_max = compute_cl(flapped_alpha_max, flapped_alpha_0, flapped_slope, flapped_a1, flapped_alpha_star)

# Create professional plot
plt.figure(figsize=(8, 6))
plt.plot(alpha_clean, clean_cl, 'b-', label='Clean Wing', linewidth=2)
plt.plot(alpha_flapped, flapped_cl, 'r-', label='Fowler-Flapped Wing', linewidth=2)

# Mark key points
plt.plot(clean_alpha_0, 0, 'bo', label='Clean: α₀', markersize=8)
plt.plot(clean_alpha_max, clean_cl_max, 'b^', label='Clean: C_L,max', markersize=8)
plt.plot(flapped_alpha_0, 0, 'ro', label='Flapped: α₀', markersize=8)
plt.plot(flapped_alpha_max, flapped_cl_max, 'r^', label='Flapped: C_L,max', markersize=8)

# Plot settings
plt.xlabel('Angle of Attack, α (degrees)', fontsize=12)
plt.ylabel('Lift Coefficient, C_L', fontsize=12)
plt.title('Lift Coefficient vs. Angle of Attack for Clean and Fowler-Flapped Wings', fontsize=14)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(fontsize=10)
plt.axhline(0, color='k', linestyle='-', alpha=0.3)
plt.axvline(0, color='k', linestyle='-', alpha=0.3)

# Adjust layout and save
plt.tight_layout()
plt.savefig('lift_curves.png', dpi=300, bbox_inches='tight')
plt.close()