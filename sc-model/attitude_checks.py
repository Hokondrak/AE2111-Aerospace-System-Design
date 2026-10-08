"""
Verification and validation of attitude_sim.py. Running this file runs the sim (on import)
and checks its output against conservation laws, closed-form results and the independent
worst-case torque table in torques.py. Prints PASS/FAIL per check.
"""

import numpy as np
from scipy.spatial.transform import Rotation as Rot

import constants as C
import torques as tq
import attitude_sim as sim

I = sim.inertia
dt = sim.dt
omega = sim.rate_log                                  # body rates [rad/s], one row per step
T = sim.T_log                                         # total torque [Nm], body axes
attitude = Rot.from_euler("XYZ", sim.attitude_log)    # body -> star axes, per step
results = []


def check(name, value, limit, detail):
    results.append((name, value <= limit, detail))


# 1. Angular momentum balance (verifies Euler's equation and the body/star frame handling):
#    in star axes, H(t) - H(0) must equal the integral of the torque.
H = attitude.apply(omega @ I.T)                       # I @ omega, rotated to star axes
dH_sim = H - H[0]
dH_torque = np.vstack((np.zeros(3), np.cumsum(attitude.apply(T)[:-1] * dt, axis=0)))
err = np.linalg.norm(dH_sim - dH_torque, axis=1).max() / np.linalg.norm(dH_sim, axis=1).max()
check("Momentum balance", err, 0.01, f"residual {err:.2%} of the largest momentum change")

# 2. Energy balance: E(t) - E(0) must equal the work done, the integral of omega . T.
E = 0.5 * np.einsum("ij,jk,ik->i", omega, I, omega)
dE_sim = E - E[0]
dE_work = np.r_[0.0, np.cumsum(np.einsum("ij,ij->i", omega, T)[:-1] * dt)]
err = np.abs(dE_sim - dE_work).max() / np.abs(dE_sim).max()
check("Energy balance", err, 0.01, f"residual {err:.2%} of the largest energy change")

# 3. Eclipse fraction against the cylindrical-shadow result asin(R/r) / pi.
expected = np.arcsin(C.MERCURY_RADIUS / sim.r) / np.pi
err = abs(sim.eclipse_log.mean() - expected)
check("Eclipse fraction", err, 0.005,
      f"sim {sim.eclipse_log.mean():.2%}, analytic {expected:.2%}")

# 4. Gravity gradient at t = 0 (exactly nadir pointing) against 3 n^2 (z x I z).
gg_expected = 3 * sim.dn**2 * np.array([-I[1, 2], I[0, 2], 0.0])
gg_sim = sim.torque_arrays["Gravity gradient"][0]
err = np.linalg.norm(gg_sim - gg_expected) / np.linalg.norm(gg_expected)
check("Gravity gradient at t = 0", err, 1e-6,
      f"sim {np.linalg.norm(gg_sim):.3e} Nm, analytic {np.linalg.norm(gg_expected):.3e} Nm")

# 5. No torque may exceed the independent worst-case (SMAD) envelope for the Operations phase.
envelope = tq.PHASES[3]["torques"]
for name, values in sim.torque_arrays.items():
    peak = np.linalg.norm(values, axis=1).max()
    ratio = peak / envelope[name][3]
    check(f"Envelope: {name}", ratio, 1.0, f"peak {peak:.3e} Nm = {ratio:.0%} of worst case")


if __name__ == "__main__":
    width = max(len(name) for name, _, _ in results)
    for name, ok, detail in results:
        print(f"  [{'PASS' if ok else 'FAIL'}]  {name:{width}}  {detail}")
    print(f"\n  {sum(ok for _, ok, _ in results)}/{len(results)} checks passed")
