import math
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np


def plot_bearing_feasibility(N, t2, stress_grid, sigma_critical, M, w, Fx, Fy):
  """Plots a discrete feasibility grid for bearing stress across combinations of N and t2.

  Colors cells green if bearing stress < sigma_critical, and red otherwise.
  """
  N_grid, T_grid = np.meshgrid(N, t2)
  works_grid = stress_grid < sigma_critical

  fig, ax = plt.subplots(figsize=(9, 6))
  cmap = mcolors.ListedColormap(['#e74c3c', '#2ecc71'])

# Plot discrete cells centered on each (n, t2) pair
  ax.pcolormesh(
      N_grid,
      T_grid,
      works_grid.astype(int),
      cmap=cmap,
      vmin=0,  # Forces 0 (False) -> Red
      vmax=1,  # Forces 1 (True) -> Green
      shading='nearest',
      edgecolors='white',
      linewidth=1.5,
      alpha=0.85,
  )

  # Annotate each cell with its bearing stress value (MPa)
  for i in range(len(t2)):
    for j in range(len(N)):
      ax.text(
          N[j],
          t2[i],
          f'{stress_grid[i, j]:.0f}',
          ha='center',
          va='center',
          color='black',
          fontsize=8,
          fontweight='bold',
      )

  # Plot the analytical critical threshold curve
  n_fine = np.linspace(N[0], N[-1], 200)
  D_fine = w / (2.5 * n_fine + 0.5)
  P_i_fine = np.sqrt((Fx / (2 * M * n_fine)) ** 2 + (Fy / (2 * M * n_fine)) ** 2)
  t_crit = P_i_fine / (D_fine * sigma_critical)
  ax.plot(n_fine, t_crit, color='black', linestyle='--', linewidth=2)

  # Axis formatting
  ax.set_xticks(N)
  ax.set_yticks(t2)
  step_t = t2[1] - t2[0] if len(t2) > 1 else 0.05
  ax.set_ylim(t2[0] - step_t / 2, t2[-1] + step_t / 2)
  ax.set_xlabel('Number of Fasteners (n)', fontsize=12)
  ax.set_ylabel('Thickness t2 (mm)', fontsize=12)
  ax.set_title(
      f'Bearing Stress Feasibility for M = {M} (Values = Stress in MPa)',
      fontsize=13,
  )

  # Legend
  legend_handles = [
      plt.Rectangle(
          (0, 0),
          1,
          1,
          color='#2ecc71',
          alpha=0.85,
          label=f'Works (< {sigma_critical} MPa)',
      ),
      plt.Rectangle(
          (0, 0),
          1,
          1,
          color='#e74c3c',
          alpha=0.85,
          label=f'Fails (>= {sigma_critical} MPa)',
      ),
      plt.Line2D(
          [0],
          [0],
          color='black',
          linestyle='--',
          linewidth=2,
          label='Critical Threshold',
      ),
  ]
  ax.legend(handles=legend_handles, loc='upper right')

  plt.tight_layout()
  plt.show()


# --- Main Calculation ---
#CAN BE CHANGED
M = 1 # Number of columns (only for one side) 
w = 2.5
sigma_critical = 103

g = 9.81
J = 1.5


Fy = 4.53 * 2 * g * J
Fz = 4.53 * 6 * g * J
P = math.sqrt((100 / 99) * (Fy**2 + Fz**2))
Fx = P / 10

N = np.arange(1, 10)
t2 = np.arange(1, 10)*0.2

# Compute 2D bearing stress array (rows = t2, cols = N)
N_grid, T_grid = np.meshgrid(N, t2)
D_grid = w / (2.5 * N_grid + 0.5)
Number_fasteners = 2 * M * N_grid
P_i_grid = np.sqrt(
    (Fx / Number_fasteners) ** 2 + (Fy / Number_fasteners) ** 2
)
bearing_stress_grid = P_i_grid / (D_grid * T_grid)

# Call the plotting function
plot_bearing_feasibility(
    N, t2, bearing_stress_grid, sigma_critical, M, w, Fx, Fy
)