from Parameters import *
import numpy as np
import multiprocessing

NUM_TO_ALPH_DICT = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E', 6: 'F', 7: 'G', 8: 'H', 9: 'I', 10: 'J', 11: 'K',
                    12: 'L', 13: 'M',
                    14: 'N', 15: 'O', 16: 'P', 17: 'Q', 18: 'R', 19: 'S', 20: 'T', 21: 'U', 22: 'V', 23: 'W',
                    24: 'X', 25: 'Y', 26: 'Z', }

""" Constants """
AMU_SM149 = 148.917192
AMU_U235 = 235.043930
AMU_U238 = 238.050788
AMU_PU239 = 239.052163
AMU_ZR = 91.224
AMU_H = 1.00794
AVO = 6.022e23  # avogadro's number
RATIO_HZR = 1.575  # TS allows 1.55 to 1.60. This is an ATOM ratio
BETA_EFF = 0.0075
CM_PER_INCH = 2.54
CM_PER_PERCENT_HEIGHT = 0.38
MEV_PER_KELVIN = 8.617328149741e-11
REACT_ADD_RATE_LIMIT_DOLLARS = 0.16

""" ENDF/B-VIII.0 libraries from LA-UR-20-30460 """

U235_TEMPS_K_XS_DICT = {294: '92235.00c',
                        600: '92235.01c',
                        900: '92235.02c',
                        1200: '92235.03c',
                        2500: '92235.04c',
                        0.1: '92235.05c',
                        250: '92235.06c'}

U238_TEMPS_K_XS_DICT = {294: '92238.00c',
                        600: '92238.01c',
                        900: '92238.02c',
                        1200: '92238.03c',
                        2500: '92238.04c',
                        0.1: '92238.05c',
                        250: '92238.06c'}

PU239_TEMPS_K_XS_DICT = {294: '94239.00c',
                         600: '94239.01c',
                         900: '94239.02c',
                         1200: '94239.03c',
                         2500: '94239.04c',
                         0.1: '94239.05c',
                         250: '94239.06c', }

SM149_TEMPS_K_XS_DICT = {294: '62149.00c',
                         600: '62149.01c',
                         900: '62149.02c',
                         1200: '62149.03c',
                         2500: '62149.04c',
                         0.1: '62149.05c',
                         250: '62149.06c', }

ZR_TEMPS_K_XS_DICT = {294: '40000.66c',
                      300: '40000.56c',
                      587: '40000.58c'}

H_TEMPS_K_XS_DICT = {294: '1001.00c',
                     600: '1001.01c',
                     900: '1001.02c',
                     1200: '1001.03c',
                     2500: '1001.04c',
                     0.1: '1001.05c',
                     250: '1001.06c'}

O_TEMPS_K_XS_DICT = {294: '8016.00c',
                     600: '8016.01c',
                     900: '8016.02c',
                     1200: '8016.03c',
                     2500: '8016.04c',
                     0.1: '8016.05c',
                     250: '8016.06c'}

H_ZR_TEMPS_K_SAB_DICT = {294: 'h-zrh.40t',
                         400: 'h-zrh.41t',
                         500: 'h-zrh.42t',
                         600: 'h-zrh.43t',
                         700: 'h-zrh.44t',
                         800: 'h-zrh.45t',
                         1000: 'h-zrh.46t',
                         1200: 'h-zrh.47t'}

ZR_H_TEMPS_K_SAB_DICT = {294: 'zr-zrh.40t',
                         400: 'zr-zrh.41t',
                         500: 'zr-zrh.42t',
                         600: 'zr-zrh.43t',
                         700: 'zr-zrh.44t',
                         800: 'zr-zrh.45t',
                         1000: 'zr-zrh.46t',
                         1200: 'zr-zrh.47t'}

H2O_TEMPS_K_SAB_DICT = {294: 'h-h2o.40t',
                        284: 'h-h2o.41t',
                        300: 'h-h2o.42t',
                        324: 'h-h2o.43t',
                        350: 'h-h2o.44t',
                        374: 'h-h2o.45t',
                        400: 'h-h2o.46t',
                        424: 'h-h2o.47t',
                        450: 'h-h2o.48t',
                        474: 'h-h2o.49t',
                        500: 'h-h2o.50t',
                        524: 'h-h2o.51t',
                        550: 'h-h2o.52t',
                        574: 'h-h2o.53t',
                        600: 'h-h2o.54t',
                        624: 'h-h2o.55t',
                        650: 'h-h2o.56t',
                        800: 'h-h2o.57t', }

def find_closest_value(K, lst):
    return lst[min(range(len(lst)), key=lambda i: abs(lst[i] - K))]

def get_tasks():
    cores = multiprocessing.cpu_count()
    tasks = input(f" How many CPU cores should be used? Free: {cores}. Use: ")
    if not tasks:
        print(f' The number of tasks is set to the available number of cores: {cores}.')
        tasks = cores
    else:
        try:
            tasks = int(tasks)
            if tasks < 1 or tasks > multiprocessing.cpu_count():
                raise
        except:
            print(f' Number of tasks is inappropriate. Using maximum number of CPU cores: {cores}')
            tasks = cores
    return tasks  # Integer between 1 and total number of cores available.


def h2o_temp_K_interpolate_mat(h2o_temp_K):
    """
    This function interpolates cross-sections

    example outputs:
    print(h2o_interpolate_mat(333.15)) # C = 60, K = 333.15
    >>> 1001.80c 1.698993390597    1001.81c 0.301006609403
    print(h2o_interpolate_mat(250)) # C= -23.15, K = 250
    >>> 1001.86c  2.000000000000

    ref:
    https://mcnp.lanl.gov/pdf_files/la-ur-08-5891.pdf
    pg 73
    """
    K = float('{:.2f}'.format(h2o_temp_K))
    # round to 2 decimal places to avoid floating point errors
    # rounding to < 2 digits causes errors, since there is a dictionary for K = 0.1

    T_1, T_2 = None, None

    for T in list(H_TEMPS_K_XS_DICT.keys()):
        # print(T, K)
        if T == K:
            h2o_mat_lib_1, h2o_at_frac_1 = H_TEMPS_K_XS_DICT[T], 2
            h2o_mats_interpolated = f"{h2o_mat_lib_1}  {'{:.6f}'.format(h2o_at_frac_1)}"
            return h2o_mats_interpolated

        elif T < K:
            if not T_1 or T > T_1:
                T_1 = T
                h2o_mat_lib_1 = H_TEMPS_K_XS_DICT[T_1]

        elif T > K:
            if not T_2 or T < T_2:
                T_2 = T
                h2o_mat_lib_2 = H_TEMPS_K_XS_DICT[T_2]

    h2o_at_frac_2 = 2 * ((np.sqrt(K) - np.sqrt(T_1)) / (np.sqrt(T_2) - np.sqrt(T_1)))
    h2o_at_frac_1 = 2 - h2o_at_frac_2
    h2o_mats_interpolated = f"{h2o_mat_lib_1} {'{:.6f}'.format(h2o_at_frac_1)}    {h2o_mat_lib_2} {'{:.6f}'.format(h2o_at_frac_2)}"

    return h2o_mats_interpolated


def interpolate_mat(frac, temp, xs_dict):
    """
    This function interpolates cross-sections

    example outputs:
    print(h2o_interpolate_mat(333.15)) # C = 60, K = 333.15
    >>> 1001.80c 1.698993390597    1001.81c 0.301006609403
    print(h2o_interpolate_mat(250)) # C= -23.15, K = 250
    >>> 1001.86c  2.000000000000

    ref:
    https://mcnp.lanl.gov/pdf_files/la-ur-08-5891.pdf
    pg 73
    """
    K = float('{:.2f}'.format(float(temp)))
    frac = float('{:.6f}'.format(float(frac)))
    # round to 2 decimal places to avoid floating point errors
    # rounding to < 2 digits causes errors, since there is a dictionary for K = 0.1

    T_1, T_2 = None, None

    for T in list(xs_dict.keys()):
        if T == K:
            lib_1, frac_1 = xs_dict[T], frac
            mat_interpolated_str = f"{lib_1}  {'{:.6f}'.format(frac_1)}"
            return mat_interpolated_str

        elif T < K:
            if not T_1 or T > T_1:
                T_1 = T
                lib_1 = xs_dict[T_1]

        elif T > K:
            if not T_2 or T < T_2:
                T_2 = T
                lib_2 = xs_dict[T_2]

    frac_2 = 2 * ((np.sqrt(K) - np.sqrt(T_1)) / (np.sqrt(T_2) - np.sqrt(T_1)))
    frac_1 = 2 - frac_2
    mat_interpolated_str = f"{lib_1} {'{:.6f}'.format(frac_1)}    {lib_2} {'{:.6f}'.format(frac_2)}"

    return mat_interpolated_str

def find_h2o_temp_K_density(K):
    try:
        C = float('{:.2f}'.format(float(K)-273))
        density = float('{:.6f}'.format((
            999.83952
            +16.945176*C
            -7.9870401e-3*C**2
            -46.170461e-6*C**3
            +105.56302e-9*C**4
            -280.54253e-12*C**5)/(1+16.897850e-3*C)/1000))
        print(f"\n   comment. at {C} C, h2o density was calculated to be {density} g/cc ")
        # Equation for water density given temperature in C, works for 0 to 150 C at 1 atm
        # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4909168/

        if C < 0 or C > 150:
            print(f"\n   warning. h2o has calculated density {density} g/cc at given temp {C} C, ")
            print(f"   warning. but that is outside the range 0 - 150 C safely predicted by the formula ")
        return density

    except:
        print(f"\n   fatal. finding h2o density for temperature {K} K failed")
        print(f"   fatal. ensure you are inputing a numeric-only str, float, or int into the function")