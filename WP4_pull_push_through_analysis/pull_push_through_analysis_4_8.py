# This Function returns the relevant values for Pull and Push Through Analysis as a List
# def pull_push_through_analysis():
#     return

# This function returns the Force per individual fastener as a function of F_y and n_f (the number of fasteners)
def F_pi(F_y, n_f):
    return F_y / n_f


# This funciton returns the force an individual fastener experiences due to M_z
# M_z is the moment through the z direction, A_i is the shear Area of the respective Fastener, r_i is the distance from the center of the fastener to the center of gravity of the entire plate
# n_f is the number of fasteners
def F_p_Mz(M_z, A_i, r_i, n_f):
    sigma_Ai_r_i_squared = 0
    for i in range(n_f):
        sigma_Ai_r_i_squared = sigma_Ai_r_i_squared + A_i * r_i**2
    return M_z * A_i * r_i / sigma_Ai_r_i_squared


# This function returns the total force an individual fastener experiences
def F_pi_total(F_pi, F_p_Mz):
    return F_pi + F_p_Mz
