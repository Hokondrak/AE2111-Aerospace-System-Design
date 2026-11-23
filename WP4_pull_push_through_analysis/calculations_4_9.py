import numpy as np
import matplotlib as plt
# from .pull_push_through_analysis_4_8 import *


# This function takes the calculated pull through shear tau_pt as input and a safety_factor with values between a and b as input
# The output is the tau allowable
def tau_allowable(tau_pt, safety_factor):
    return tau_pt / safety_factor


# This function is the simplified derived version of equation 4.8 from the reader of WP4 .
# It returns the pull through shear load (simplified)
def simplified_tau_pt(yield_shear_stress):
    return yield_shear_stress / (3**0.5)


def A_shear_backplate(D_fi_backplate, thickness_backplate):
    return np.pi * D_fi_backplate * thickness_backplate


def A_shear_spacecraft_wall(D_fi_spacecraft_wall, thickness_spacecraft_wall):
    return np.pi * D_fi_spacecraft_wall * thickness_spacecraft_wall


def tau_backplate(F_pt_backplate, A_shear_backplate):
    return F_pt_backplate / A_shear_backplate


def tau_spacecraft_wall(F_pt_sc_wall, A_shear_spacecraft_wall):
    return F_pt_sc_wall / A_shear_spacecraft_wall


# input: [[fastener_index, F_yi_total, F_pi, F_p_Mz_i], ...]
def whatIsAbsMaxF_yi(finalList):
    max = 0
    for i in range(len(finalList)):
        temp = ((finalList[i][1]) ** 2) ** 0.5
        if temp >= max:
            max = temp
    return max


def marginOfSafety(tau_allowable, tau_pt):
    return tau_allowable / tau_pt - 1


# Returns a list like the following:
# [[tau_pt_force, tau_allowable_material, isAllowable]]
# input: [D_fi, thickness, F_pt_max, safety_factor, yield_shear_stress]
def is_tau_allowable(inputList):
    D_fi = inputList[0]
    thickness = inputList[1]
    F_pt_max = inputList[2]
    safety_factor = inputList[3]
    yield_shear_stress = inputList[4]

    isAllowable = False
    A_shear = np.pi * D_fi * thickness
    tau_pt_force = F_pt_max / A_shear
    tau_pt_material = yield_shear_stress / (3**0.5)
    tau_allowable_material = tau_pt_material / safety_factor
    if tau_allowable_material < tau_pt_force:
        isAllowable = False
    else:
        isAllowable = True
    return [[tau_pt_force, tau_allowable_material, isAllowable]]


def toString(is_tau_allowable_list):
    outputString = f"tau pull through load: {is_tau_allowable_list[0][0]} --- allowable material tau: {is_tau_allowable_list[0][1]} --- is Allowable?: {is_tau_allowable_list[0][2]}\n"
    return outputString


# input: [D_fi, thickness, F_pt_max, safety_factor, yield_shear_stress]
input = [1, 2, 3, 4, 5]
print(toString(is_tau_allowable(input)))
