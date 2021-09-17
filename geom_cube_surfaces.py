import numpy as np


def main():
    chain_interval = 18.5  # input('Input desired axial interval between cubes in cm: ')
    inner_tank_height = 164
    desired_num_cubes_on_chain_b = 7
    desired_num_cubes_on_chain_a = 8
    first_cube_offset = 1.25
    """
    Core 6
    first_cube_offset = 0.3
    """
    cube_length = 5
    cube_diagonal = cube_length * np.sqrt(2)

    """
    DESIRED MCNP CODE OUTPUT FORM
    
    c center at z = 148.678932
    811 p  0  1 1 152.214466
    812 p  0 -1 1 152.214466
    813 p  0  1 1 145.143398
    814 p  0 -1 1 145.143398 
    """

    cube_number = 0
    eight_cube_chain_code = ''
    eight_cube_chain_center_heights = []

    while cube_number < desired_num_cubes_on_chain_b:
        cube_number += 1
        cube_center_height = inner_tank_height - chain_interval * (cube_number - 1) - cube_diagonal / 2 * cube_number \
                             - first_cube_offset - (chain_interval + cube_diagonal) / 2
        cube_top_height = cube_center_height + 5 * np.sqrt(2) / 2
        cube_bot_height = cube_center_height - 5 * np.sqrt(2) / 2
        new_code = f"c center at z = {round(cube_center_height, 6)}\n" \
                   f"8{cube_number}1 p  0   1  1  {round(cube_top_height, 6)}\n" \
                   f"8{cube_number}2 p  0  -1  1  {round(cube_top_height, 6)}\n" \
                   f"8{cube_number}3 p  0   1  1  {round(cube_bot_height, 6)}\n" \
                   f"8{cube_number}4 p  0  -1  1  {round(cube_bot_height, 6)}\n"
        eight_cube_chain_center_heights.append(round(cube_center_height, 6))
        eight_cube_chain_code = f"{eight_cube_chain_code}c\nc ------ Cube {cube_number} ------ \n{new_code}"

    eight_cube_chain_code = eight_cube_chain_code + 'c\nc 8-cube chain center z coordinates\nc ' + str(
        eight_cube_chain_center_heights)

    cube_number = 0
    nine_cube_chain_code = ''
    nine_cube_chain_center_heights = []

    while cube_number < desired_num_cubes_on_chain_a:
        cube_number += 1
        cube_center_height = inner_tank_height - chain_interval * (cube_number - 1) - cube_diagonal / 2 * cube_number \
                             - first_cube_offset
        cube_top_height = cube_center_height + 5 * np.sqrt(2) / 2
        cube_bot_height = cube_center_height - 5 * np.sqrt(2) / 2
        new_code = f"c center at z = {round(cube_center_height, 6)}\n" \
                   f"9{cube_number}1 p  0   1  1  {round(cube_top_height, 6)}\n" \
                   f"9{cube_number}2 p  0  -1  1  {round(cube_top_height, 6)}\n" \
                   f"9{cube_number}3 p  0   1  1  {round(cube_bot_height, 6)}\n" \
                   f"9{cube_number}4 p  0  -1  1  {round(cube_bot_height, 6)}\n"
        nine_cube_chain_center_heights.append(round(cube_center_height, 6))
        nine_cube_chain_code = f"{nine_cube_chain_code}c\nc ------ Cube {cube_number} ------ \n{new_code}"

    nine_cube_chain_code = nine_cube_chain_code + 'c\nc 9-cube chain center z coordinates\nc ' + str(
        nine_cube_chain_center_heights)

    print(eight_cube_chain_code)
    print(nine_cube_chain_code)
    # print(first_cube_offset)


if __name__ == "__main__":
    main()
