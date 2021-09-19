import matplotlib.pyplot as plt  # plotting library
import numpy as np  # vector and matrix math library
import pandas as pd  # data analysis and manipulation tool
import sys  # system-specific parameters and functions
from sys import platform  # to find os platform for geom_plotter ghostscript command
import os  # miscellaneous operating system interfaces
from jinja2 import Template  # templating language
import fnmatch
import traceback, sys
import shutil
import platform
import json
import glob
import getpass
import math
import xlrd, openpyxl
import multiprocessing
from datetime import datetime
from Parameters import *
from Utilities import *


class MCNP_File:

    def __init__(self,
                 run_type,
                 tasks,
                 print_input=True,  # default: only defines self variables and does not print input template
                 core_number=49,  # default: reads fuel load positions from ./Source/Core/49.core
                 delete_extensions=['.s'],  # default: '.s'
                 r_tank=62, # cm
                 h_tank=119.8, # cm
                 n_rings=5,
                 chains_per_ring=[6,12,16,20,24],
                 ring_radii_list=None,
                 n_cubes_chain_a=9,
                 n_cubes_chain_b=8,
                 cube_interval=5.5,
                 first_cube_offset=5.5,
                 h2o_temp_K=294,  # used in: rcty, 293 K = 20 C = room temp = default temp in mcnp
                 h2o_density=None,  # used in: rcty, set None to calculate h2o_density from h2o_temp_K (recommended)
                 h2o_void_percent=0,  #
                 d2o_temp_K=294,  # used in: rcty, 293 K = 20 C = room temp = default temp in mcnp
                 d2o_density=None,  # used in: rcty, set None to calculate h2o_density from h2o_temp_K (recommended)
                 d2o_void_percent=0,  #
                 d2o_purity=96.8,  # at% d2o
                 fuel_temp_K=294,  # used in: rcty
                 fuel_density=19.05, # 19.05 g/cc nominal density
                 grph_density=1.8, # 1.80 g/cc nominal density w air gaps
                 ):

        """
        Define core parameters
        """
        self.print_input = print_input
        self.datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.run_type = run_type
        self.tasks = tasks
        self.core_number = core_number
        self.delete_extensions = delete_extensions
        self.username = getpass.getuser()

        ''' Core geometric properties'''
        self.r_tank, self.h_tank, self.n_rings = r_tank, h_tank, n_rings # tank radius (cm), height (cm), number of fuel rings
        self.chains_per_ring = chains_per_ring
        self.ring_radii_list = ring_radii_list
        self.cube_interval = cube_interval
        self.n_cubes_chain_a, self.n_cubes_chain_b = n_cubes_chain_a, n_cubes_chain_b
        self.first_cube_offset = first_cube_offset

        ''' Heavy and light water moderator properties '''
        self.h2o_temp_K = h2o_temp_K
        self.h2o_void_percent = h2o_void_percent

        if not h2o_density:
            self.h2o_density = (1 - 0.01 * self.h2o_void_percent) * find_h2o_temp_K_density(
                h2o_temp_K)  # if h2o_density == None, calculate density from temp
        else:
            self.h2o_density = (1 - 0.01 * self.h2o_void_percent) * h2o_density

        ''' Fuel properties'''
        self.fuel_density = fuel_density
        self.fuel_temp_K = fuel_temp_K
        # self.add_samarium = add_samarium # no samarium in haigerloch fuel cubes

        ''' Other properties '''
        self.grph_density = grph_density

        """
        Find data libraries
        """
        self.find_xs_libs()
        self.find_sab_libs()


        """
        Add tallies to end of input file (to allow substitution into tally definition)
        """
        if run_type in ['flux', 'powr']:
            with open(f'./Source/tallies/{self.run_type}.tal', 'r') as tally_file:
                tally_str = tally_file.read()
        else:
            tally_str = ''

        """
        Define and create necessary directories
        """
        self.template_filepath = f"./Source/haigerloch.template"
        self.MCNP_folder = f'./MCNP/{run_type}'
        self.results_folder = f'./Results/{run_type}'
        self.temp_folder = f'{self.MCNP_folder}/temp'
        self.user_temp_folder = f'{self.temp_folder}/{self.username}'
        self.inputs_folder = f"{self.MCNP_folder}/inputs"
        self.outputs_folder = f"{self.MCNP_folder}/outputs"

        self.create_paths()

        """
        Write code
        """
        self.write_setup()
        self.core_cells = self.write_core_cells()
        self.chain_a_surfaces, self.chain_b_surfaces = self.write_cube_surfaces()
        self.core_fuel_cells_complements = self.write_cells_complements_str()
        self.ksrc_card = self.write_ksrc_card()
        print(self.core_fuel_cells_complements)

        """
        Load variables into dictionary to be pasted into the template
        """
        self.parameters = {'datetime': self.datetime,
                           'run_type': self.run_type,
                           # 'run_desc': RUN_DESCRIPTIONS_DICT[self.run_type],
                           'core_number': self.core_number,
                           # 'core_config': self.core_config_dict,
                           'core_fuel_cells_complements': self.core_fuel_cells_complements,
                           'core_fuel_cells': self.core_cells,
                           # 'chain_a_cube_cells_complements': self.chain_a_cube_cells_complements,
                           # 'chain_b_cube_cells_complements': self.chain_b_cube_cells_complements,
                           'chain_a_surfaces': self.chain_a_surfaces,
                           'chain_b_surfaces': self.chain_b_surfaces,
                           'tally': 'c ',
                           'mode': ' n ',
                           'grph_density': f'-{self.grph_density}', # -wt, +at
                           'h2o_density': f'-{self.h2o_density}',  # - for mass density, + for atom density
                           'd2o_density': f'-{self.h2o_density}',  # - for mass density, + for atom density
                           'h_mats': self.h2o_mat_interpolated_str,
                           'o_xs_lib': self.o_xs_lib,
                           'h2o_sab_lib': self.h2o_sab_lib,
                           'h2o_temp_MeV': '{:.6e}'.format(self.h2o_temp_K * MEV_PER_KELVIN),
                           'fuel_temp_MeV': '{:.6e}'.format(self.fuel_temp_K * MEV_PER_KELVIN),
                           # 'fuel_mats': self.fuel_mat_cards, # all cubes uniform
                           'ksrc_card': self.ksrc_card,
                           'n_per_cycle': 20000, # 20k for testing, 100k for production
                           'discard_cycles': 15,
                           'kcode_cycles': 115,
                           }

        """
        Define input file names and paths
        """
        self.base_filename = f"{self.template_filepath.split('/')[-1].split('.')[0]}_core{self.core_number}"
        ''' no samarium in haigerloch 
        if not self.add_samarium:
            self.base_filename = f"{self.template_filepath.split('/')[-1].split('.')[0]}_core{self.core_number}_nosm149"
        else:
            self.base_filename = f"{self.template_filepath.split('/')[-1].split('.')[0]}_core{self.core_number}"
        '''

        if self.run_type in ['base','sdm', 'cxs']:
            self.input_filename = f"{self.base_filename}_{self.run_type}" \
                                  f".i"

        else:
            self.input_filename = f"{self.base_filename}_{self.run_type}" \
                                  f"_a{str(self.parameters['safe_height']).zfill(3)}" \
                                  f"_h{str(self.parameters['shim_height']).zfill(3)}" \
                                  f"_r{str(self.parameters['reg_height']).zfill(3)}.i"

        self.input_filepath = f"{self.user_temp_folder}/{self.input_filename}"
        self.output_filename = f"o_{self.input_filename.split('.')[0]}.o"
        self.output_filepath = f"{self.MCNP_folder}/outputs/{self.output_filename}"

        if self.run_type == 'prnt':
            self.input_filepath = f"{self.results_folder}/{self.input_filename}"

        """
        Create input file by populating template with self.parameters dictionary
        """
        if self.print_input:
            with open(self.template_filepath, 'r') as template_file:
                template_str = template_file.read()
                template = Template(template_str + '\n' + tally_str)
                template.stream(**self.parameters).dump(self.input_filepath)
                self.print_input = False
                print(f"\n input file created at: {self.input_filepath}")








    def write_setup(self):
        self.ring_number_list = np.arange(1, self.n_rings + 1)
        if self.ring_radii_list is None:
            self.ring_radii_list = []
            for ring_number in self.ring_number_list:
                radius_increment = self.r_tank / (self.n_rings + 1)
                new_radius = radius_increment * ring_number
                self.ring_radii_list.append(round(new_radius, 6))

        self.cube_coords_all_list = []
        for r in self.ring_radii_list:
            n_cubes_this_chain = int(self.chains_per_ring[self.ring_radii_list.index(r)])
            cube_coords_this_ring_list = []
            for pos in np.arange(0, n_cubes_this_chain):
                angle = 0 + 2 * np.pi / n_cubes_this_chain * pos + np.pi / 2  # phase shift to begin at (0,y) and not (x, 0)
                x = str("{:.6f}".format(r * np.cos(angle)))
                y = str("{:.6f}".format(r * np.sin(angle)))
                if not x.startswith("-"): x = '+' + x
                if not y.startswith("-"): y = '+' + y
                cube_coords_this_ring_list.append([x, y])
            self.cube_coords_all_list.append(cube_coords_this_ring_list)

    def write_core_cells(self):
        cell_lines = f"c {self.ring_radii_list}\nc"
        for ring_number in self.ring_number_list:
            ring_index = int(ring_number - 1)
            n_cubes_this_chain = int(self.chains_per_ring[ring_index])
            for pos in np.arange(0, n_cubes_this_chain):
                if (ring_number + 1) % 2 != 0:  # for odd rings, the 1st position starts with Chain B
                    if (pos + 1) % 2 != 0:  #
                        line = f"{int(ring_number) + 1}{str(pos + 1).zfill(3)} 0 +10 -11 -40 trcl=({self.cube_coords_all_list[ring_index][pos][0]} {self.cube_coords_all_list[ring_index][pos][1]} 0) imp:n=1 fill=80"
                    else:
                        line = f"{int(ring_number) + 1}{str(pos + 1).zfill(3)} 0 +10 -11 -40 trcl=({self.cube_coords_all_list[ring_index][pos][0]} {self.cube_coords_all_list[ring_index][pos][1]} 0) imp:n=1 fill=90"
                else:
                    if (pos + 1) % 2 != 0:  #
                        line = f"{int(ring_number) + 1}{str(pos + 1).zfill(3)} 0 +10 -11 -40 trcl=({self.cube_coords_all_list[ring_index][pos][0]} {self.cube_coords_all_list[ring_index][pos][1]} 0) imp:n=1 fill=90"
                    else:
                        line = f"{int(ring_number) + 1}{str(pos + 1).zfill(3)} 0 +10 -11 -40 trcl=({self.cube_coords_all_list[ring_index][pos][0]} {self.cube_coords_all_list[ring_index][pos][1]} 0) imp:n=1 fill=80"
                cell_lines = '\n'.join([cell_lines, line])
        return cell_lines

    def write_cells_complements_str(self):
        complement_str = "           "
        counter = 0
        for p in self.chains_per_ring:
            for pos in list(range(1, p + 1)):
                if counter < 4:
                    new_complement_str = f"#{self.chains_per_ring.index(p) + 2}0{str(pos).zfill(2)}"
                    complement_str = f"{complement_str} {new_complement_str}"
                    counter += 1
                elif counter >= 4:
                    new_complement_str = f"#{self.chains_per_ring.index(p) + 2}0{str(pos).zfill(2)}"
                    complement_str = f"{complement_str}\n            {new_complement_str}"
                    counter = 1
        return complement_str

    def write_cube_surfaces(self):
        cube_number = 0
        chain_b_code = ''
        self.chain_b_cubes_center_heights = []
        while cube_number < self.n_cubes_chain_b:
            cube_number += 1
            cube_center_height = self.h_tank - (self.first_cube_offset + CUBE_DIAGONAL / 2
                                           + (self.cube_interval + CUBE_DIAGONAL) / 2) \
                                 - (cube_number - 1) * (self.cube_interval + CUBE_DIAGONAL)
            # cube_center_height = inner_tank_height - chain_interval * (cube_number - 1) - cube_diagonal / 2 * cube_number \
            #                      - first_cube_offset - (chain_interval + cube_diagonal) / 2
            cube_top_height = cube_center_height + 5 * np.sqrt(2) / 2
            cube_bot_height = cube_center_height - 5 * np.sqrt(2) / 2
            new_code = f"c center at z = {round(cube_center_height, 6)}\n" \
                       f"8{cube_number}1 p  0   1  1  {round(cube_top_height, 6)}\n" \
                       f"8{cube_number}2 p  0  -1  1  {round(cube_top_height, 6)}\n" \
                       f"8{cube_number}3 p  0   1  1  {round(cube_bot_height, 6)}\n" \
                       f"8{cube_number}4 p  0  -1  1  {round(cube_bot_height, 6)}\n"
            self.chain_b_cubes_center_heights.append(round(cube_center_height, 6))
            chain_b_code = f"{chain_b_code}c\nc ------ Cube {cube_number} ------ \n{new_code}"
        chain_b_code = chain_b_code + 'c\nc 8-cube chain center z coordinates\nc ' + str(
            self.chain_b_cubes_center_heights)

        cube_number = 0
        chain_a_code = ''
        self.chain_a_cubes_center_heights = []
        while cube_number < self.n_cubes_chain_a:
            cube_number += 1
            cube_center_height = self.h_tank - (self.first_cube_offset + CUBE_DIAGONAL / 2) - (cube_number - 1) * \
                                 (self.cube_interval + CUBE_DIAGONAL)
            # cube_center_height = inner_tank_height - chain_interval * (cube_number - 1) - cube_diagonal / 2 * cube_number \
            #                      - first_cube_offset
            cube_top_height = cube_center_height + 5 * np.sqrt(2) / 2
            cube_bot_height = cube_center_height - 5 * np.sqrt(2) / 2
            new_code = f"c center at z = {round(cube_center_height, 6)}\n" \
                       f"9{cube_number}1 p  0   1  1  {round(cube_top_height, 6)}\n" \
                       f"9{cube_number}2 p  0  -1  1  {round(cube_top_height, 6)}\n" \
                       f"9{cube_number}3 p  0   1  1  {round(cube_bot_height, 6)}\n" \
                       f"9{cube_number}4 p  0  -1  1  {round(cube_bot_height, 6)}\n"
            self.chain_a_cubes_center_heights.append(round(cube_center_height, 6))
            chain_a_code = f"{chain_a_code}c\nc ------ Cube {cube_number} ------ \n{new_code}"
        chain_a_code = chain_a_code + 'c\nc 9-cube chain center z coordinates\nc ' + str(
            self.chain_a_cubes_center_heights)

        return chain_b_code, chain_a_code # i fucked up so the chain_b_code is code for chain A, vice versa

    def write_core_fuel_cells(self):
        pass

    def write_ksrc_card(self):
        ksrc_lines = "ksrc"
        test_counter = 0
        indent_space = "      "
        ring_number_list = np.arange(1, self.n_rings + 1)
        for ring_number in ring_number_list:
            ring_index = int(ring_number - 1)
            number_of_points = int(self.chains_per_ring[ring_index])
            for pos in np.arange(0, number_of_points):
                if ring_number % 2 == 0:
                    if (pos + 1) % 2 == 0:
                        for z in self.chain_a_cubes_center_heights:
                            z = str("{:.6f}".format(z))
                            if not z.startswith("-"): z = '+' + z
                            line = f"{indent_space} {self.cube_coords_all_list[ring_index][pos][0]} {self.cube_coords_all_list[ring_index][pos][1]} {z}"
                            ksrc_lines = '\n'.join([ksrc_lines, line])
                            test_counter += 1
                    else:
                        for z in self.chain_b_cubes_center_heights:
                            z = str("{:.6f}".format(z))
                            if not z.startswith("-"): z = '+' + z
                            line = f"{indent_space} {self.cube_coords_all_list[ring_index][pos][0]} {self.cube_coords_all_list[ring_index][pos][1]} {z}"
                            ksrc_lines = '\n'.join([ksrc_lines, line])
                            test_counter += 1
                else:
                    if (pos + 1) % 2 == 0:
                        for z in self.chain_b_cubes_center_heights:
                            z = str("{:.6f}".format(z))
                            if not z.startswith("-"): z = '+' + z
                            line = f"{indent_space} {self.cube_coords_all_list[ring_index][pos][0]} {self.cube_coords_all_list[ring_index][pos][1]} {z}"
                            ksrc_lines = '\n'.join([ksrc_lines, line])
                            test_counter += 1
                    else:
                        for z in self.chain_a_cubes_center_heights:
                            z = str("{:.6f}".format(z))
                            if not z.startswith("-"): z = '+' + z
                            line = f"{indent_space} {self.cube_coords_all_list[ring_index][pos][0]} {self.cube_coords_all_list[ring_index][pos][1]} {z}"
                            ksrc_lines = '\n'.join([ksrc_lines, line])
                            test_counter += 1
        return ksrc_lines

    def create_paths(self, paths_to_create=None):
        """
        Assign filepaths and create directories if they do not exist
        """
        if not paths_to_create:
            paths_to_create = [self.MCNP_folder, self.inputs_folder, self.outputs_folder,
                               self.temp_folder, self.user_temp_folder,
                               self.results_folder]  # order matters here

        if os.path.exists(self.user_temp_folder):
            shutil.rmtree(self.user_temp_folder)

        for path in paths_to_create:
            if not os.path.exists(path):
                try:
                    os.mkdir(path)
                except:
                    print(f"\n   warning. cannot make {path}")
                    print(f"   warning. It is possible that the directories above the destination do not exist.")
                    print(f"   warning. Python cannot create multiple directory levels in one command.")

    def find_xs_libs(self):
        """
        find mat libraries for fuel isotopes
        """
        mat_list = [[None, U235_TEMPS_K_XS_DICT, 'U-235'],
                    [None, U238_TEMPS_K_XS_DICT, 'U-238'],
                    # [None, PU239_TEMPS_K_XS_DICT, 'Pu-239'], # no fission products or zirconium in haigerloch
                    # [None, SM149_TEMPS_K_XS_DICT, 'Sm-149'],
                    # [None, ZR_TEMPS_K_XS_DICT, 'zirconium'],
                    [None, H_TEMPS_K_XS_DICT, 'hydrogen'],  # used in fuel mats, NOT when interpolating h mats
                    [None, O_TEMPS_K_XS_DICT, 'oxygen'], ]  # used in light water mat, EVEN WHEN interpolating h mats

        for i in range(0, len(mat_list)):
            try:
                mat_list[i][0] = mat_list[i][1][self.fuel_temp_K]
            except:
                closest_temp_K = find_closest_value(self.fuel_temp_K, list(mat_list[i][1].keys()))
                mat_list[i][0] = mat_list[i][1][closest_temp_K]
                print(f"\n   comment. {mat_list[i][2]} cross-section (xs) data at {self.fuel_temp_K} K does not exist")
                print(f"   comment.   using closest available xs data at temperature: {closest_temp_K} K")

        self.u235_xs_lib, self.u238_xs_lib, = mat_list[0][0], mat_list[1][0],
        # self.pu239_xs_lib, self.sm149_xs_lib = mat_list[2][0], mat_list[3][0]
        # self.zr_xs_lib,  = mat_list[4][0]
        self.h_xs_lib, self.o_xs_lib = mat_list[2][0], mat_list[3][0]  # KEEP

        """
        find mat libraries for light water isotopes
        """
        self.h2o_mat_interpolated_str = h2o_temp_K_interpolate_mat(self.h2o_temp_K)  # Utilities.py
        try:
            self.o_xs_lib = O_TEMPS_K_XS_DICT[self.h2o_temp_K]
        except:
            closest_temp_K = find_closest_value(self.h2o_temp_K, list(O_TEMPS_K_XS_DICT.keys()))
            self.o_xs_lib = O_TEMPS_K_XS_DICT[closest_temp_K]
            print(f"\n   comment. oxygen cross-section (xs) data at {self.h2o_temp_K} K does not exist")
            print(f"   comment.   using closest available xs data at temperature: {closest_temp_K} K")

    def find_sab_libs(self):
        # find mt libraries
        # zr mt lib not available

        try:
            self.h2o_sab_lib = H2O_TEMPS_K_SAB_DICT[self.h2o_temp_K]
        except:
            closest_temp_K = find_closest_value(self.h2o_temp_K, list(H2O_TEMPS_K_SAB_DICT.keys()))
            self.h2o_sab_lib = H2O_TEMPS_K_SAB_DICT[closest_temp_K]
            print(f"\n   comment. light water scattering S(a,B) data at {self.h2o_temp_K} K does not exist")
            print(f"   comment.   using closest available S(a,B) data at temperature: {closest_temp_K} K")

        mt_list = [[None, ZR_H_TEMPS_K_SAB_DICT, 'zr_h'],
                   [None, H_ZR_TEMPS_K_SAB_DICT, 'h_zr']]

        for i in range(0, len(mt_list)):
            try:
                mt_list[i][0] = mt_list[i][1][self.fuel_temp_K]
            except:
                closest_temp_K = find_closest_value(self.fuel_temp_K, list(mt_list[i][1].keys()))
                mt_list[i][0] = mt_list[i][1][closest_temp_K]
                print(f"\n   comment. {mt_list[i][2]} scattering S(a,B) data at {self.fuel_temp_K} does not exist")
                print(f"   comment.   using closest available S(a,B) data at temperature: {closest_temp_K} K")

        self.zr_h_sab_lib, self.h_zr_sab_lib = mt_list[0][0], mt_list[1][0]

    def move_mcnp_files(self, output_types_to_move=['.o', '.r', '.s', '.msht']):
        """ Moves files to appropriate folder.
        """
        # move input
        src, dst = self.user_temp_folder, self.inputs_folder
        shutil.move(self.input_filepath, os.path.join(dst, self.input_filename))

        # move outputs
        output_file = f"{self.output_filename.split('.')[0]}"  # general output filename without extension
        dst = self.outputs_folder

        """ instead of programming it here, just define which outputs to move when function is called in NeutronicsEngine.py
        if self.run_type in ['banked', 'kntc', 'rodcal', 'rcty','sdm']:
            output_types_to_move = ['.o']
        elif self.run_type == 'plot':
            output_types_to_move = ['.ps']
        """

        if not self.mcnp_skipped:
            for extension in output_types_to_move:
                try:
                    filename = output_file + extension
                    shutil.move(os.path.join(src, filename), os.path.join(dst, filename))
                    print(f'\n   comment. moved {filename}')
                    print(f'   comment.   from {src} ')
                    print(f'   comment.   to   {dst}\n')
                except:
                    print(f'   warning. error moving {filename}')
                    print(f'   warning.   from {src} ')
                    print(f'   warning.   to   {dst}')

    def delete_mcnp_files(self, folder=None, extensions_to_delete=None):
        # Default args are False unless specified in command
        # NB: os.remove(f'*.r') does not work bc os.remove does not take wildcards (*)
        if not folder:
            folder = self.user_temp_folder

        if not extensions_to_delete:
            if self.run_type in ['plot']:
                extensions_to_delete = ['.c', '.o', '.s']
            else:
                extensions_to_delete = ['.r', '.s']

        for ext in extensions_to_delete:
            for file in glob.glob(f'{folder}/*{ext}'):
                try:
                    os.remove(file)
                except:
                    print(f"\n   comment. did not remove {f'{folder}/{file}'}")
                    print(f"   comment.   because the filepath does not exist")

    def run_mcnp(self):
        """
        Runs MCNP
        """
        if self.output_filename not in os.listdir(self.outputs_folder):
            os.system(
                f"""mcnp6 i="{self.input_filepath}" n="{self.user_temp_folder}/{self.output_filename.split('.')[0]}." tasks {self.tasks}""")
            self.mcnp_skipped = False
        else:
            print(f'\n   comment. skipping this mcnp run since results for {self.input_filename} already exist.')
            self.mcnp_skipped = True



    def extract_keff(self):
        """
        Parses output file for neutron multiplication factor, keff, and its uncertainty.
        """
        if os.path.exists(self.results_folder):
            try:
                get_keff = False
                found_keff = False
                with open(self.output_filepath) as f:
                    for line in f:
                        if found_keff:
                            return
                        else:
                            if line.startswith(" the estimated average keffs"):
                                get_keff = True
                            elif get_keff and line.startswith("       col/abs/trk len"):
                                self.keff, self.keff_unc = float(line.split()[2]), float(line.split()[3])
                                found_keff = True
                                print(f' keff: {self.keff} +/- {self.keff_unc}')
            except:
                print(f"\n   warning. keff not found in {self.output_filepath}")
                print(f"   warning.   skipping {self.output_filepath}")
        else:
            print(f'\n   fatal. cannot find {self.results_folder}\n')
            sys.exit(2)

    def run_geometry_plotter(self, debug=False):
        """
            Plots geometry to file, converts PostScript file to tiff, crops images
        """
        outputs_dir = self.outputs_folder
        results_dir = self.results_folder
        plotcom_path = f"./Source/Plot/plotCommandsToFile"
        for filepath in [results_dir, f"{results_dir}/full", f"{results_dir}/cropped_scale",
                         f"{results_dir}/cropped_no_scale"]:
            if not os.path.exists(filepath):
                os.mkdir(filepath)

        ps_name = f'o_{self.base_filename}.ps'
        tiff_name = f'o_{self.base_filename}.tiff'
        print(os.getcwd())

        if not debug:
            if ps_name not in os.listdir(outputs_dir):
                os.system(
                    f'mcnp6 ip i="{self.input_filepath}" n="{self.user_temp_folder}/o_{self.base_filename}." tasks {self.tasks} plotm={f"{self.user_temp_folder}/plotm"} com={plotcom_path}')
                self.delete_mcnp_files(self.user_temp_folder, self.delete_extensions)
                os.rename(f"{self.user_temp_folder}/plotm.ps", f"{self.user_temp_folder}/{ps_name}")
                self.move_mcnp_files()

            # ghostscript command is 'gs' for Linux, Mac
            # and 'gswin64.exe' or 'gswin32.exe' for Windows 64 and 32
            # you may have to change the path variables to call 'gs' from cmd
            print(f" operating system identified as: {platform.system()}")
            if platform.system().lower().startswith('win32'):
                os.system(
                    f'gswin32.exe -sDEVICE=tiff24nc -r300 -sOutputFile={results_dir}/{tiff_name} -dBATCH -dNOPAUSE {results_dir}/{ps_name}')
            elif platform.system().lower().startswith('win62') or platform.system().lower().startswith('windows'):
                os.system(
                    f'gswin64.exe -sDEVICE=tiff24nc -r300 -sOutputFile={results_dir}/{tiff_name} -dBATCH -dNOPAUSE {results_dir}/{ps_name}')
            else:
                os.system(
                    f'gs -sDEVICE=tiff24nc -r300 -sOutputFile={results_dir}/{tiff_name} -dBATCH -dNOPAUSE {results_dir}/{ps_name}')

            if tiff_name in os.listdir(results_dir):
                from PIL import Image, ImageSequence, ImageDraw, ImageFont
                image_names = ['reflector_xy',
                               'reflector_yz',
                               'reflector_zoomed_xy',
                               'reflector_zoomed_yz',
                               'core_xy',
                               'core_yz',
                               'controlrod_xy',
                               'controlrod_yz',
                               'rabbit_xy',
                               'rabbit_big_yz',
                               'rabbit_small_yz',
                               'lazysusan_xy',
                               'lazysusan_yz',
                               'ambe_xy',
                               'ambe_yz',
                               'ambe_zoomed_yz',
                               'ir192_xy',
                               'ir192_yz',
                               'ir192_zoomed_yz',
                               'core_comp_xy',
                               'core_comp_yz',
                               'core_load_xy',
                               'core_load_yz',
                               'reflector_comp_xy',
                               'reflector_comp_yz',
                               'reflector_comp_zoomed_xy',
                               'reflector_comp_zoomed_yz',
                               'reflector_load_xy',
                               'reflector_load_yz',
                               'reflector_load_zoomed_xy',
                               'reflector_load_zoomed_yz',
                               ]

                with Image.open(f"{outputs_dir}/{tiff_name}") as im:
                    for name, frame in zip(image_names, ImageSequence.Iterator(im)):
                        frame = frame.rotate(270, expand=True)
                        # frame = frame.crop((450,780,2480,2910))
                        if '_xy' in name:
                            xlabel, ylabel = "x (cm)", "y (cm)"
                        if '_yz' in name:
                            xlabel, ylabel = "y (cm)", "z (cm)"
                        if '_xz' in name:
                            xlabel, ylabel = "x (cm)", "z (cm)"
                        font = ImageFont.truetype(f"./Source/Plot/NotoMono-Regular.ttf", 36)
                        ImageDraw.Draw(frame).text((1960, 2300), xlabel, fill=(0, 0, 0), font=font, align='center')
                        frame = frame.rotate(-90, resample=0, expand=1, center=None, translate=None, fillcolor=None)
                        ImageDraw.Draw(frame).text((1200, 975), ylabel, fill=(0, 0, 0), font=font)
                        frame = frame.rotate(90, resample=0, expand=1, center=None, translate=None, fillcolor=None)
                        frame.save(f'{results_dir}/full/1_{name}.png')

                        # actual plot area is 1880 x 1880
                        frame = frame.crop(
                            (970, 300, 3000, 2360))  # (left, top, right, bottom) # coordinates of cropped image
                        frame.save(f'{results_dir}/cropped_scale/2_{name}.png')

                        frame = frame.crop(
                            (115, 35, 1995, 1915))  # (left, top, right, bottom) # coordinates of cropped image
                        frame.save(f'{results_dir}/cropped_no_scale/3_{name}.png')

        else:
            os.system(f'mcnp6 ip i="{self.input_file}" n={self.user_temp_folder}o_plot. com=./src/mcnp/plotCommands')