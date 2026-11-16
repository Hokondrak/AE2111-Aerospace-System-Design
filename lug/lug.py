import np


###Inputs
#Force
f_y = None
f_z = None
m_x = None

#Geometry
y = None
l = None
A = None
w = None


#MoI
I_p = None
I = None

#Geometry Coeffs.
k_e = None

length = np.arrange(0,l,1)

###


sig_x = (m_x * y)/I_p

sig_y = (0.5 * f_y)/(k_e * A)

sig_z = (f_z * 0.5 * length * 0.5 * w)/ I