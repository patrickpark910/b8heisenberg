import sys

import numpy as np


def main():

    R_fuel = 4.4
    cube_length = 5
    cube_diagonal = cube_length * np.sqrt(2)

    # Core 2A
    # R_outer = 62
    # N = 5
    # P = [6,12,16,20,24]
    # ring_radii_list = None
    # KSRC_8_Z = [148.678932, 136.107864, 123.536797, 110.965729, 98.394661, 85.823593, 76.002525, 60.681458]
    # KSRC_9_Z = [154.964196, 142.393398, 129.982233, 117.251263, 104.680195, 92.109127, 79.538059, 66.966992, 54.395924]

    # Core 2B
    # R_outer = 62
    # N = 5
    # P = [6,12,16,20,24]
    # ring_radii_list = None
    # KSRC_8_Z = [145.928932, 127.857864, 109.786797, 91.715729, 73.644661, 55.573593, 37.502525, 19.431458]
    # KSRC_9_Z = [154.964466, 136.893398, 118.82233, 100.751263, 82.680195, 64.609127, 46.538059, 28.466991, 10.395924]

    # Core 4
    # R_outer = 62
    # N = 5
    # P = [6,12,16,20,24]
    # ring_radii_list = None
    # KSRC_8_Z = [151.428932, 138.857864, 126.286797, 113.715729, 101.144661, 88.573593, 76.002525, 63.431458, 50.86039, 38.289322, 25.718254]
    # KSRC_9_Z = [157.714466, 145.143398, 132.57233, 120.001263, 107.430195, 94.859127, 82.288059, 69.716991, 57.145924, 44.574856, 32.003788, 19.43272]

    # Core 5
    # R_outer = 62
    # N = 5
    # P = [6,12,18,24,30]
    # ring_radii_list = None
    # KSRC_8_Z = [151.428932, 138.857864, 126.286797, 113.715729, 101.144661, 88.573593, 76.002525, 63.431458, 50.86039, 38.289322, 25.718254]
    # KSRC_9_Z = [157.714466, 145.143398, 132.57233, 120.001263, 107.430195, 94.859127, 82.288059, 69.716991, 57.145924, 44.574856, 32.003788, 19.43272]

    # Core 6
    # R_outer = 62
    # N = 5
    # P = [6,12,16,20,24]
    # ring_radii_list = None
    # KSRC_8_Z = [148.628932, 129.093398, 109.557864, 90.02233, 70.486797, 50.951263, 31.415729, 11.880195]
    # KSRC_9_Z = [160.164466, 140.628932, 121.093398, 101.557864, 82.02233, 62.486797, 42.951263, 23.415729, 3.880195]

    # Core 7
    # R_outer = 62
    # N = 5
    # P = [6,12,16,20,24]
    # ring_radii_list = None
    # KSRC_8_Z = [146.428932, 124.393398, 102.357864, 80.32233, 58.286797, 36.251263, 14.215729]
    # KSRC_9_Z = [159.214466, 137.178932, 115.143398, 93.107864, 71.07233, 49.036797, 27.001263, 4.965729]

    """ Core 8
    R_tank = 72.3333
    N = 5
    P = [6, 12, 16, 20, 24]
    ring_radii_list = None
    chain_interval = 16  # input('Input desired axial interval between cubes in cm: ')
    inner_tank_height = 164
    desired_num_cubes_on_chain_b = 8
    desired_num_cubes_on_chain_a = 9
    first_cube_offset = 0.3
    """

    """ Core 9 
    R_tank = 72.3333
    N = 6
    P = [6, 12, 16, 20, 24, 30]
    ring_radii_list = None
    chain_interval = 16  # input('Input desired axial interval between cubes in cm: ')
    inner_tank_height = 164
    desired_num_cubes_on_chain_b = 8
    desired_num_cubes_on_chain_a = 9
    first_cube_offset = 0.3
    """

    """ Core 10
    R_tank = 72.3333
    N = 6
    P = [6, 12, 16, 20, 24, 30]
    ring_radii_list = None
    chain_interval = 13.5  # input('Input desired axial interval between cubes in cm: ')
    inner_tank_height = 164
    desired_num_cubes_on_chain_b = 9
    desired_num_cubes_on_chain_a = 10
    first_cube_offset = 2.5
    """

    """ Core 16
    R_tank = 72.3333
    N = 6
    P = [6, 12, 16, 20, 24, 30]
    ring_radii_list = None
    chain_interval = 12.5  # input('Input desired axial interval between cubes in cm: ')
    inner_tank_height = 270
    desired_num_cubes_on_chain_b = 10
    desired_num_cubes_on_chain_a = 11
    first_cube_offset = chain_interval
    """

    """ Core 17 
    R_tank = 72.3333
    N = 6
    P = [6, 12, 16, 20, 24, 30]
    ring_radii_list = None
    chain_interval = 16  # input('Input desired axial interval between cubes in cm: ')
    inner_tank_height = 270
    desired_num_cubes_on_chain_b = 10
    desired_num_cubes_on_chain_a = 11
    first_cube_offset = 16
    """

    """ Core 18 
    R_tank = 72.3333
    N = 6
    P = [6, 12, 16, 20, 24, 30]
    ring_radii_list = None
    chain_interval = 9  # input('Input desired axial interval between cubes in cm: ')
    inner_tank_height = 270
    desired_num_cubes_on_chain_b = 10
    desired_num_cubes_on_chain_a = 11
    first_cube_offset = 9
    """

    """ Core 19
    R_tank = 72.3333
    N = 6
    P = [6, 12, 16, 20, 24, 30]
    ring_radii_list = None
    chain_interval = 5.5  # input('Input desired axial interval between cubes in cm: ')
    inner_tank_height = 270
    desired_num_cubes_on_chain_b = 10
    desired_num_cubes_on_chain_a = 11
    first_cube_offset = chain_interval
    """

    """ Core 20 
    R_tank = 72.3333
    N = 6
    P = [6, 12, 16, 20, 24, 30]
    ring_radii_list = None
    chain_interval = 9.5  # input('Input desired axial interval between cubes in cm: ')
    inner_tank_height = 270
    desired_num_cubes_on_chain_b = 10
    desired_num_cubes_on_chain_a = 11
    first_cube_offset = chain_interval
    """

    """ Core 21 
    R_tank = 72.3333
    N = 6
    P = [6, 12, 16, 20, 24, 30]
    ring_radii_list = None # [10.809523, 21.619046, 32.428569, 43.238091, 54.047614, 64.857137]
    chain_interval = 8.5  # input('Input desired axial interval between cubes in cm: ')
    inner_tank_height = 270
    desired_num_cubes_on_chain_b = 10
    desired_num_cubes_on_chain_a = 11
    first_cube_offset = chain_interval
    """

    """ Core 22 
    R_tank = 72.3333
    N = 6
    P = [6, 12, 16, 20, 24, 30]
    ring_radii_list = None # [10.809523, 21.619046, 32.428569, 43.238091, 54.047614, 64.857137]
    chain_interval = 8.0  # input('Input desired axial interval between cubes in cm: ')
    inner_tank_height = 270
    desired_num_cubes_on_chain_b = 10
    desired_num_cubes_on_chain_a = 11
    first_cube_offset = chain_interval
    """

    """ Core 23 
    R_tank = 72.3333
    N = 6
    P = [6, 12, 16, 20, 24, 30]
    ring_radii_list = None # [10.809523, 21.619046, 32.428569, 43.238091, 54.047614, 64.857137]
    chain_interval = 7.5  # input('Input desired axial interval between cubes in cm: ')
    inner_tank_height = 270
    desired_num_cubes_on_chain_b = 10
    desired_num_cubes_on_chain_a = 11
    first_cube_offset = chain_interval
    """

    """ Core 24
    R_tank = 72.3333
    N = 6
    P = [6, 12, 16, 20, 24, 30]
    ring_radii_list = None # [10.809523, 21.619046, 32.428569, 43.238091, 54.047614, 64.857137]
    chain_interval = 7.0  # input('Input desired axial interval between cubes in cm: ')
    inner_tank_height = 270
    desired_num_cubes_on_chain_b = 10
    desired_num_cubes_on_chain_a = 11
    first_cube_offset = chain_interval
    """

    """ Core 24 
    R_tank = 72.3333
    N = 6
    P = [6, 12, 16, 20, 24, 30]
    ring_radii_list = [10.809523, 21.619046, 32.428569, 43.238091, 54.047614, 64.857137]
    chain_interval = 7.75  # input('Input desired axial interval between cubes in cm: ')
    inner_tank_height = 270
    desired_num_cubes_on_chain_b = 10
    desired_num_cubes_on_chain_a = 11
    first_cube_offset = chain_interval
    """

    """ Core 28 """
    R_tank = 168.777777
    N = 14
    P = [6, 12, 16, 20, 24, 30, 36, 42, 50, 58, 64, 74, 84, 94]
    ring_radii_list = None
    chain_interval = 7.75  # input('Input desired axial interval between cubes in cm: ')
    inner_tank_height = 270
    desired_num_cubes_on_chain_b = 10
    desired_num_cubes_on_chain_a = 11
    first_cube_offset = chain_interval

    if len(P) != int(N):
        print("You have not properly specified how many points you want to determine for each ring.")
        sys.exit()

    """ This section writes the surface code for each chain
    Ex. 
    c center at z = 148.678932
    811 p  0  1 1 152.214466
    812 p  0 -1 1 152.214466
    813 p  0  1 1 145.143398
    814 p  0 -1 1 145.143398 
    """

    complement_str = ""
    counter = 1
    for p in P:
        for pos in list(range(1, p+1)):
            if counter < 4:
                new_complement_str = f"#{P.index(p)+2}0{str(pos).zfill(2)}"
                complement_str = f"{complement_str} {new_complement_str}"
                counter += 1
            elif counter >= 4:
                new_complement_str = f"#{P.index(p)+2}0{str(pos).zfill(2)}"
                complement_str = f"{complement_str}\n{new_complement_str}"
                counter = 1
    print(complement_str)

    cube_number = 0
    chain_b_code = ''
    chain_b_center_heights = []

    while cube_number < desired_num_cubes_on_chain_b:
        cube_number += 1
        cube_center_height = inner_tank_height - (first_cube_offset + cube_diagonal / 2
                                                  + (chain_interval + cube_diagonal) / 2) \
                             - (cube_number - 1) * (chain_interval + cube_diagonal)
        # cube_center_height = inner_tank_height - chain_interval * (cube_number - 1) - cube_diagonal / 2 * cube_number \
        #                      - first_cube_offset - (chain_interval + cube_diagonal) / 2
        cube_top_height = cube_center_height + 5 * np.sqrt(2) / 2
        cube_bot_height = cube_center_height - 5 * np.sqrt(2) / 2
        new_code = f"c center at z = {round(cube_center_height, 6)}\n" \
                   f"8{cube_number}1 p  0   1  1  {round(cube_top_height, 6)}\n" \
                   f"8{cube_number}2 p  0  -1  1  {round(cube_top_height, 6)}\n" \
                   f"8{cube_number}3 p  0   1  1  {round(cube_bot_height, 6)}\n" \
                   f"8{cube_number}4 p  0  -1  1  {round(cube_bot_height, 6)}\n"
        chain_b_center_heights.append(round(cube_center_height, 6))
        chain_b_code = f"{chain_b_code}c\nc ------ Cube {cube_number} ------ \n{new_code}"

    chain_b_code = chain_b_code + 'c\nc 8-cube chain center z coordinates\nc ' + str(
        chain_b_center_heights)

    cube_number = 0
    chain_a_code = ''
    chain_a_center_heights = []

    while cube_number < desired_num_cubes_on_chain_a:
        cube_number += 1
        cube_center_height = inner_tank_height - (first_cube_offset + cube_diagonal / 2) - (cube_number - 1) * \
                             (chain_interval + cube_diagonal)
        # cube_center_height = inner_tank_height - chain_interval * (cube_number - 1) - cube_diagonal / 2 * cube_number \
        #                      - first_cube_offset
        cube_top_height = cube_center_height + 5 * np.sqrt(2) / 2
        cube_bot_height = cube_center_height - 5 * np.sqrt(2) / 2
        new_code = f"c center at z = {round(cube_center_height, 6)}\n" \
                   f"9{cube_number}1 p  0   1  1  {round(cube_top_height, 6)}\n" \
                   f"9{cube_number}2 p  0  -1  1  {round(cube_top_height, 6)}\n" \
                   f"9{cube_number}3 p  0   1  1  {round(cube_bot_height, 6)}\n" \
                   f"9{cube_number}4 p  0  -1  1  {round(cube_bot_height, 6)}\n"
        chain_a_center_heights.append(round(cube_center_height, 6))
        chain_a_code = f"{chain_a_code}c\nc ------ Cube {cube_number} ------ \n{new_code}"

    chain_a_code = chain_a_code + 'c\nc 9-cube chain center z coordinates\nc ' + str(
        chain_a_center_heights)

    """ This section sets up the variable values necessary for future sections
    
    Ex. For R = 6, N = 2, P = [2, 4]
    print(ring_radii_list)
    >>> [2.0, 4.0]
    print(cords_list_all)
    >>> [[[0.0, 2.0], [-0.0, -2.0]], [[0.0, 4.0], [-4.0, 0.0], [-0.0, -4.0], [4.0, -0.0]]]
    """
    ring_number_list = np.arange(1, N + 1)
    if ring_radii_list is None:
        ring_radii_list = []
        for ring_number in ring_number_list:
            radius_increment = R_tank / (N + 1)
            new_radius = radius_increment * ring_number
            ring_radii_list.append(round(new_radius, 6))

    coords_list_all = []

    for r in ring_radii_list:
        number_of_points = int(P[ring_radii_list.index(r)])
        coords_list_for_this_ring = []
        for pos in np.arange(0, number_of_points):
            angle = 0 + 2 * np.pi / number_of_points * pos + np.pi / 2  # phase shift to begin at (0,y) and not (x, 0)
            x = str("{:.6f}".format(r * np.cos(angle)))
            y = str("{:.6f}".format(r * np.sin(angle)))
            if not x.startswith("-"): x = '+' + x
            if not y.startswith("-"): y = '+' + y
            coords_list_for_this_ring.append([x, y])
        coords_list_all.append(coords_list_for_this_ring)

    """ This section writes the cell code for the Core Fuel Positions
    Ex:
    c B ring
    2001 0 +10 -11 -40 trcl=(+0.000000 +10.333333 0) imp:n=1 fill=90
    2002 0 +10 -11 -40 trcl=(-8.948929 +5.166667 0) imp:n=1 fill=80
    2003 0 +10 -11 -40 trcl=(-8.948929 -5.166666 0) imp:n=1 fill=90
    2004 0 +10 -11 -40 trcl=(-0.000000 -10.333333 0) imp:n=1 fill=80
    """
    cell_lines = f"c {ring_radii_list}\nc"
    for ring_number in ring_number_list:
        ring_index = int(ring_number - 1)
        number_of_points = int(P[ring_index])
        for pos in np.arange(0, number_of_points):
            if (ring_number + 1) % 2 != 0:  # for odd rings, the 1st position starts with Chain B
                if (pos + 1) % 2 != 0:  #
                    line = f"{int(ring_number) + 1}{str(pos + 1).zfill(3)} 0 +10 -11 -40 trcl=({coords_list_all[ring_index][pos][0]} {coords_list_all[ring_index][pos][1]} 0) imp:n=1 fill=80"
                else:
                    line = f"{int(ring_number) + 1}{str(pos + 1).zfill(3)} 0 +10 -11 -40 trcl=({coords_list_all[ring_index][pos][0]} {coords_list_all[ring_index][pos][1]} 0) imp:n=1 fill=90"
            else:
                if (pos + 1) % 2 != 0:  #
                    line = f"{int(ring_number) + 1}{str(pos + 1).zfill(3)} 0 +10 -11 -40 trcl=({coords_list_all[ring_index][pos][0]} {coords_list_all[ring_index][pos][1]} 0) imp:n=1 fill=90"
                else:
                    line = f"{int(ring_number) + 1}{str(pos + 1).zfill(3)} 0 +10 -11 -40 trcl=({coords_list_all[ring_index][pos][0]} {coords_list_all[ring_index][pos][1]} 0) imp:n=1 fill=80"
            cell_lines = '\n'.join([cell_lines, line])

    """ This section writes the surface code for the Core Fuel Positions
    Ex:
    602001 c/z +0.000000 +10.333333 +4.4 $ B1
    602002 c/z -8.948929 +5.166667 +4.4 $ B2
    602003 c/z -8.948929 -5.166666 +4.4 $ B3
    602004 c/z -0.000000 -10.333333 +4.4 $ B4
    
    surf_lines = "c {cell} c/z {x} {y} {r} \nc Core position holes for fuel universes"
    for ring_number in ring_number_list:
        ring_index = int(ring_number - 1)
        number_of_points = int(P[ring_index])
        for pos in np.arange(0, number_of_points):
            line = f"6{str(int(ring_number) + 1).zfill(2)}{str(pos + 1).zfill(3)} " \
                   f"c/z " \
                   f"{coords_list_all[ring_index][pos][0]} {coords_list_all[ring_index][pos][1]} +{R_fuel} " \
                   f"$ {num_to_alph_dict[ring_number + 1]}{pos + 1}"
            surf_lines = '\n'.join([surf_lines, line])
    """

    """ This section writes the KSRC code for the Source Neutron Coordinates
    Ex. 
    c Source neutron coordinates
    ksrc +0.000000 +10.333333 +157.714466
         +0.000000 + 10.333333 + 145.143398
         +0.000000 + 10.333333 + 132.572330
    """

    ksrc_lines = "c"
    test_counter = 0
    indent_space = "      "
    for ring_number in ring_number_list:
        ring_index = int(ring_number - 1)
        number_of_points = int(P[ring_index])
        for pos in np.arange(0, number_of_points):
            if ring_number % 2 == 0:
                if (pos + 1) % 2 == 0:
                    for z in chain_a_center_heights:
                        z = str("{:.6f}".format(z))
                        if not z.startswith("-"): z = '+' + z
                        line = f"{indent_space} {coords_list_all[ring_index][pos][0]} {coords_list_all[ring_index][pos][1]} {z}"
                        ksrc_lines = '\n'.join([ksrc_lines, line])
                        test_counter += 1
                else:
                    for z in chain_b_center_heights:
                        z = str("{:.6f}".format(z))
                        if not z.startswith("-"): z = '+' + z
                        line = f"{indent_space} {coords_list_all[ring_index][pos][0]} {coords_list_all[ring_index][pos][1]} {z}"
                        ksrc_lines = '\n'.join([ksrc_lines, line])
                        test_counter += 1
            else:
                if (pos + 1) % 2 == 0:
                    for z in chain_b_center_heights:
                        z = str("{:.6f}".format(z))
                        if not z.startswith("-"): z = '+' + z
                        line = f"{indent_space} {coords_list_all[ring_index][pos][0]} {coords_list_all[ring_index][pos][1]} {z}"
                        ksrc_lines = '\n'.join([ksrc_lines, line])
                        test_counter += 1
                else:
                    for z in chain_a_center_heights:
                        z = str("{:.6f}".format(z))
                        if not z.startswith("-"): z = '+' + z
                        line = f"{indent_space} {coords_list_all[ring_index][pos][0]} {coords_list_all[ring_index][pos][1]} {z}"
                        ksrc_lines = '\n'.join([ksrc_lines, line])
                        test_counter += 1

    # print(cell_lines)
    # print(surf_lines) # DO NOT USE
    # print(chain_b_code)
    # print(chain_a_code)
    # print(f"{ksrc_lines}\nc {test_counter} source points")
    # print(first_cube_offset)


if __name__ == '__main__':
    main()
