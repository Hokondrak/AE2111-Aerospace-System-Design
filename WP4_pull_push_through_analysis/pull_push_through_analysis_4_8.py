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
def F_yi_total(F_pi, F_p_Mz):
    return F_pi + F_p_Mz


# This function returns a list in the following format:
# Input: [[fastener_index, A_i, r_i, F_y, M_z]] , number_of_fasteners
# [[fastener_index, F_yi_total, F_pi, F_p_Mz_i], ...]


def listOfFastenerAndPullThroughForce(fasteners_list, number_of_fasteners):
    i = 0
    finalList = []
    while i < number_of_fasteners:
        tempList = []
        tempList.append(i)
        force_yi_total_i = F_yi_total(
            F_pi(fasteners_list[i][3], number_of_fasteners),
            F_p_Mz(
                fasteners_list[i][4],
                fasteners_list[i][1],
                fasteners_list[i][2],
                number_of_fasteners,
            ),
        )
        tempList.append(force_yi_total_i)
        F_pi_i = (F_pi(fasteners_list[i][3], number_of_fasteners),)
        F_p_Mz_i = F_p_Mz(
            fasteners_list[i][4],
            fasteners_list[i][1],
            fasteners_list[i][2],
            number_of_fasteners,
        )
        tempList.append(F_pi_i)
        tempList.append(F_p_Mz_i)
        finalList.append(tempList)
        i = i + 1
    return finalList


# input: [[fastener_index, F_yi_total, F_pi, F_p_Mz_i], ...]
# This function returns the total list with final Values for F_yi_total in human readable format


def finalListToString(finalList):
    finalString = ""
    for i in range(len(finalList)):
        lineString = ""
        lineString = f"Fastener_index: {finalList[i][0]} --- Force_yi_total: {finalList[i][1]} --- F_pi: {finalList[i][2]} --- F_Mpz_i: {finalList[i][3]}"
        finalString = finalString + lineString + "\n"
    return finalString


def whatIsAbsMaxF_yi(finalList):
    max = 0
    for i in range(len(finalList)):
        temp = ((finalList[i][1]) ** 2) ** 0.5
        if temp >= max:
            max = temp
    return max


#  [[fastener_index, A_i, r_i, F_y, M_z]]
# Use this for input to get the
# Note: A_i cancels out in the formula so you can put any dummy value there
input = [
    [0, -1, 3.75 * 10 ** (-3), 88.88, 117.85],
    [1, -1, 3.75 * 10 ** (-3), 88.88, -117.85],
]

# print(listOfFastenerAndPullThroughForce(input, len(input)))
print(finalListToString(listOfFastenerAndPullThroughForce(input, len(input))))


# We could do some plotting maybe.
