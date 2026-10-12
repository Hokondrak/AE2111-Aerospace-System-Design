import numpy as np
import matplotlib.pyplot as plt
import math
import matplotlib.pyplot as plt
import math

T_max = np.array([0.0324732960, 0.0438448000, 0.0325321465])
max_torque_SF = 1.5
T_max_with_SF = max_torque_SF * T_max

h = 1
a = 1
L = np.sqrt(h*h + 9*a*a/4)
d = np.sqrt(h*h + a*a)
SQRT3 = np.sqrt(3)

#unit vectors for the reaction wheel axes:
RW1_axis = np.array([h, 0, a]) / d
RW2_axis = np.array([-h/2, SQRT3*h/2, a]) / d
RW3_axis = np.array([-h/2, -SQRT3*h/2, a]) / d
RW4_axis = np.array([0, 0, -1])

wheel_axis_matrix = np.array([RW1_axis, RW2_axis, RW3_axis, RW4_axis]).transpose()

# Draw the RW axes
"""
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
origin = np.array([0, 0, 0])
ax.quiver(*origin, *RW1_axis, color='r', label='v1')
ax.quiver(*origin, *RW2_axis, color='g', label='v2')
ax.quiver(*origin, *RW3_axis, color='b', label='v3')
ax.quiver(*origin, *RW4_axis, color='r', label='v4')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.legend()
plt.show()
"""

RW_radius = 0.1
RW_height = 0.05
RW_material_density = 2700 #aluminum, kg/m3
RW_mass = RW_material_density * math.pi * RW_radius*RW_radius * RW_height

RW_MMOI = 0.5 * RW_mass * RW_radius * RW_radius #1/2 mr^2
RW_motor_torque = 0.2 #N/m
RW_max_angular_accel = RW_motor_torque / RW_MMOI
RW_max_angular_vel = 10 #rad/s
I_w = np.array([RW_MMOI, RW_MMOI, RW_MMOI, RW_MMOI]) #array with mmoi for each rw. all the same but this array allows for them to be different

def RW_angular_accels_To_SC_torque(RW_angular_accelerations):#ang accels: rad/s/s for each RW (there are 4 RW's)
    T_sc = -wheel_axis_matrix @ (RW_MMOI * RW_angular_accelerations)
    return T_sc

def compute_RW_angular_accels_for_desired_torques(T_desired):
    B = wheel_axis_matrix @ np.diag(I_w)
    alpha = -np.linalg.pinv(B) @ T_desired
    for i in range(len(alpha)):
        a = alpha[i]
        if a > RW_max_angular_vel:
            print("alpha too high in wheel #"+str(i)+" !")
    return alpha

print(compute_RW_angular_accels_for_desired_torques(np.array([1, 0, 0])))