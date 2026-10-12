import numpy as np
import matplotlib.pyplot as plt
import math

T_max = np.array([0.0324732960, 0.0438448000, 0.0325321465])
max_torque_SF = 1.5

T_max_with_SF = max_torque_SF * T_max

h = 1
a = 1
L = math.sqrt(h*h + 9*a*a/4)
d = math.sqrt(h*h + a*a)
SQRT3 = math.sqrt(3)

RW1_axis = np.array([h, 0, a]) / d
RW2_axis = np.array([-h/2, SQRT3*h/2, a]) / d
RW3_axis = np.array([-h/2, -SQRT3*h/2, a]) / d
RW4_axis = np.array([0, 0, -1])

# Draw the vectors
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