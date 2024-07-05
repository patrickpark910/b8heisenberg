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
import multiprocessing
import linecache
from datetime import datetime
from Parameters import *
from Utilities import *
from Packing import *


class MCNP_Input:
    def __init__(self,
             run_type,
             tasks,
             n_cubes = N_CUBES,            # nominal = 664
             r_core=CORE_RADIUS,
             modr_vol = MODR_VOL,          # in cm^3 - nominal = 1400e3
             h2o_temp_K = AMBIENT_TEMP_K,  # used in: rcty, 284 K = 11 C = room temp = default temp in mcnp
             h2o_density=None,             # used in: rcty, set None to calculate h2o_density from h2o_temp_K (recommended)
             d2o_temp_K=AMBIENT_TEMP_K,    # used in: rcty, 284 K = 11 C = room temp = default temp in mcnp
             d2o_density=None,             # used in: rcty, set None to calculate h2o_density from h2o_temp_K (recommended)
             d2o_purity=D2O_PURITY,        # at% d2o
             fuel_temp_K=AMBIENT_TEMP_K,   # used in: rcty
             fuel_density=FUEL_DENSITY,    # 18.5349 g/cc from PNNL, 19.05 nominal density
             grph_density=GRPH_DENSITY, # 1.58 accounting for air gaps from Bopp and Pesic
             print_input=True,
             delete_extensions=['.s'],     # default: '.s'
             ):


        """ Define core parameters
        """
        self.print_input = print_input
        self.datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.run_type = run_type
        self.tasks = tasks
        self.delete_extensions = delete_extensions
        self.username = getpass.getuser()

        # Core geometric properties
        self.n_cubes  = n_cubes

        self.modr_vol = modr_vol
        hr_ratio = 2 # 1.82
        self.core_vol   = self.n_cubes*CUBE_LENGTH**3 + self.modr_vol # cc
        self.r_core   = (self.core_vol/hr_ratio/np.pi)**(1/3)
        self.h_core   = hr_ratio*self.r_core # 1.82*
        self.r_grph   = self.r_core +  40 # rd((GRPH_VOL * 3/(4*np.pi) + self.r_core**3)**(1/3))  
        self.h_grph   = self.h_core +  80
        self.r_lwtr   = self.r_grph +  60 # rd((GRPH_VOL * 3/(4*np.pi) + self.r_core**3)**(1/3))  
        self.h_lwtr   = self.h_grph + 120

        # D2O and H2O properties
        self.h2o_temp_K = h2o_temp_K
        if not h2o_density:
            self.h2o_density = h2o_temp_K_to_mass_density(h2o_temp_K)  # if h2o_density == None, calculate density from temp
        else:
            self.h2o_density = h2o_density

        self.d2o_temp_K = d2o_temp_K
        self.d2o_purity = d2o_purity
        if not d2o_density:
            self.d2o_density = d2o_temp_K_to_mass_density(d2o_temp_K)  # if d2o_density == None, calculate density from temp
        else:
            self.d2o_density = d2o_density

        # Fuel properties
        self.fuel_density = fuel_density
        self.fuel_temp_K = fuel_temp_K
        # self.add_samarium = add_samarium # no samarium in haigerloch fuel cubes
        self.grph_density = grph_density

        # Define and create necessary directories
        self.template_filepath = INPUT_TEMPLATE_FILEPATH 
        self.MCNP_folder = f'./MCNP/{run_type}'
        self.results_folder = f'./Results/{run_type}'
        self.temp_folder = f'{self.MCNP_folder}/temp'
        self.inputs_folder = f"{self.MCNP_folder}/inputs"
        self.outputs_folder = f"{self.MCNP_folder}/outputs"
        self.create_paths()


        """
        Define input file names and paths
        """
        self.base_filename = f"{self.template_filepath.split('/')[-1].split('.')[0]}-case{self.run_type}"
        self.input_filename = f"{self.base_filename}-c{self.n_cubes}-r{'{:.2f}'.format(self.r_core).replace('.','_')}-d2o{'{:.1f}'.format(self.d2o_purity).replace('.','_')}-v{round(self.modr_vol/1e3)}.inp"

        self.input_filepath = f"{self.temp_folder}/{self.input_filename}"
        self.output_filename = f"o_{self.input_filename.split('.')[0]}.o"
        self.output_filepath = f"{self.MCNP_folder}/outputs/{self.output_filename}"


        """ Create input file by populating template with self.parameters dictionary
        """

    def write_input(self):
        # if self.print_input:
        # print(f"\n  __MCNP_Input.py")

        # Find data libraries
        self.find_xs_libs()
        self.find_sab_libs()
        self.write_cards()

        # Load variables into dictionary to be pasted into the template
        self.parameters = {"runtype"         : self.run_type,
                           "datetime"        : self.datetime,
                           "n_cubes"         : self.n_cubes,
                           "modr_vol"        : rd(self.modr_vol/1e3),
                           "complement_cells": self.complement_cells,
                           "cube_universes"  : self.cube_universes,  
                           "r_core"          : rd(self.r_core), 
                           "h_core"          : rd(self.h_core),
                           "r_grph"          : rd(self.r_grph), 
                           "h_grph"          : rd(self.h_grph),
                           "r_lwtr"          : rd(self.r_lwtr), 
                           "h_lwtr"          : rd(self.h_lwtr),
                           "n_per_cycle"     : N_PER_CYCLE,
                           "discard_cycles"  : DISCARD_CYCLES,
                           "total_cycles"    : TOTAL_CYCLES,
                           'h2o_mats_interpolated': self.h2o_mats_interpolated_str,
                           'd2o_mats_interpolated': self.d2o_mats_interpolated_str,
                           'h_h2o_sab_lib': self.h_h2o_sab_lib,
                           'd_d2o_sab_lib': self.d_d2o_sab_lib, 
                           'o_d2o_sab_lib': self.o_d2o_sab_lib,
                           "ksrc_points"     : self.ksrc_points}

        with open(self.template_filepath, 'r') as template_file:
            template_str = template_file.read()
            template = Template(template_str) # + '\n' + tally_str)
            template.stream(**self.parameters).dump(self.input_filepath)
            self.print_input = False
            print(f"  | comment. input file created at: {self.input_filepath}")



    def write_cards(self):
        # Define the range of integers
        start, end = 201, 200+self.n_cubes

        # Define the number of integers to print per line
        self.complement_cells = '     '  # need 5 spaces
        self.ksrc_points      = ''       # need 5 spaces after first line
        self.cube_universes   = ''
        
        try:
            coords = calc_hcp_coords(self.r_core-4.5,self.n_cubes)
        except:
            print(f"  | fatal. Packing.py could not calculate hcp coords for {self.n_cubes} cubes")
            print(f"  | fatal. do not mess with Packing.py unless you understand the linear algebra")
            print(f"  | fatal. check if {round(self.modr_vol)} L > volume of {self.n_cubes} cubes")
            sys.exit(2) # fyi for testing: if sys.exit() in try clause it will still go to except

        n = 0
        for i in range(start, end + 1):

            # Print the integer to the output file
            self.complement_cells += f"#{str(i)}"
            # Check if we have printed the desired number of integers per line
            if (i - start + 1) % 6 == 0 and i != range(start, end + 1)[-1]:
                # If yes, start a new line
                self.complement_cells += f"\n     " # need 5 spaces
            else:
                # If no, add a space to separate the integers
                self.complement_cells += f" "

            coord = str(coords[n]).replace('[','').replace(']','').replace(",", " ")  

            """ Reformat and normalize coordinates with the multiplier
            # coord looks like this: 1.11 2.22 3.33
            # use rd() to make sure each component is to 6 digits """
            if n==0:
                self.cube_universes += f"{i} 0 -10 trcl=({coord}) imp:n=1 fill=1"
                self.ksrc_points += coord
            elif n>0:
                self.cube_universes += f"\n{i} 0 -10 trcl=({coord}) imp:n=1 fill=1"
                self.ksrc_points += f"\n     {coord}"  # need 5 spaces
            n += 1


        # Print the highest norm and the corresponding line
        # if line_with_highest_norm:
        #     print(f"Highest norm: {self.highest_norm}")
        #     print(f"At coords   : {line_with_highest_norm.strip()}")
        # else:
        #     print("No valid data found in the file.")

    def create_paths(self, paths_to_create=None):
        """
        Assign filepaths and create directories if they do not exist
        """
        if not paths_to_create:
            paths_to_create = [self.MCNP_folder, self.inputs_folder, self.outputs_folder,
                               self.temp_folder, self.results_folder]  # order matters here
        if os.path.exists(self.temp_folder):
            shutil.rmtree(self.temp_folder)
        for path in paths_to_create:
            if not os.path.exists(path):
                try:
                    os.mkdir(path)
                except:
                    print(f"  | warning. cannot make {path}")
                    print(f"  | warning. it is possible that the directories above the destination do not exist")
                    print(f"  | warning. python cannot create multiple directory levels in one command")


    def find_xs_libs(self):
        """
        find mat libraries for fuel isotopes
        """
        mat_list = [[None, U235_TEMPS_K_XS_DICT, 'U-235'],
                    [None, U238_TEMPS_K_XS_DICT, 'U-238'],
                    # [None, PU239_TEMPS_K_XS_DICT, 'Pu-239'], # no fission products or zirconium in B8
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
                print(f"  | comment. {mat_list[i][2]} cross-section (xs) data at {self.fuel_temp_K} K does not exist")
                print(f"  | comment.   using closest available xs data at temperature: {closest_temp_K} K")

        self.u235_xs_lib, self.u238_xs_lib, = mat_list[0][0], mat_list[1][0],
        # self.pu239_xs_lib, self.sm149_xs_lib = mat_list[2][0], mat_list[3][0]
        # self.zr_xs_lib,  = mat_list[4][0]
        self.h_xs_lib, self.o_xs_lib = mat_list[2][0], mat_list[3][0]  # KEEP

        """
        find mat libraries for water materials
        """
        self.h2o_mats_interpolated_str = wtr_interpolate_mat(self.h2o_temp_K, d2o_atom_percent=0)
        self.d2o_mats_interpolated_str = wtr_interpolate_mat(self.d2o_temp_K, d2o_atom_percent=self.d2o_purity)
        try:
            self.o_xs_lib = O_TEMPS_K_XS_DICT[self.d2o_temp_K]
        except:
            closest_temp_K = find_closest_value(self.d2o_temp_K, list(O_TEMPS_K_XS_DICT.keys()))
            self.o_xs_lib = O_TEMPS_K_XS_DICT[closest_temp_K]
            print(f"  | comment. oxygen cross-section (xs) data at {self.d2o_temp_K} K does not exist")
            print(f"  | comment.   using closest available xs data at temperature: {closest_temp_K} K")
        


    def find_sab_libs(self):
        # find mt libraries
        # zr mt lib not available
        sab_list = [[None, H2O_TEMPS_K_SAB_DICT, 'h-h2o', self.h2o_temp_K],
                   [None, D_D2O_TEMPS_K_SAB_DICT, 'd-d2o', self.d2o_temp_K],
                   [None, O_D2O_TEMPS_K_SAB_DICT, 'o-d2o', self.d2o_temp_K],]

        for i in range(0, len(sab_list)):
            try:
                sab_list[i][0] = sab_list[i][1][sab_list[i][3]]
            except:
                closest_temp_K = find_closest_value(sab_list[i][3], list(sab_list[i][1].keys()))
                sab_list[i][0] = sab_list[i][1][closest_temp_K]
                print(f"  | comment. {sab_list[i][2]} scattering S(a,B) data at {sab_list[i][3]} does not exist")
                print(f"  | comment. using closest available S(a,B) data at temperature: {closest_temp_K} K")
        self.h_h2o_sab_lib, self.d_d2o_sab_lib, self.o_d2o_sab_lib = sab_list[0][0], sab_list[1][0], sab_list[2][0]


    def move_mcnp_files(self, output_types_to_move=['.o', '.r', '.s', '.msht']):
        """ Moves files to appropriate folder.
        """
        # move input
        src, dst = self.temp_folder, self.inputs_folder
        if not os.path.exists(os.path.join(dst, self.input_filename)):
            try:
                filename = self.input_filepath.split('/')[-1]
                shutil.move(self.input_filepath, os.path.join(dst, self.input_filename))
                print(f"\n  __MCNP_Input.py"
                      f'\n  | comment. moved {filename}'
                      f'\n  | comment.   from {src} '
                      f'\n  | comment.   to   {dst}\n')
            except:
                print(f"\n  __MCNP_Input.py"
                      f'\n  | warning. error moving {filename}'
                      f'\n  | warning.   from {src} '
                      f'\n  | warning.   to   {dst}')

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
                    print(f"\n  __MCNP_Input.py"
                          f'\n  | comment. moved {filename}'
                          f'\n  | comment.   from {src} '
                          f'\n  | comment.   to   {dst}\n')
                except:
                    print(f"\n  __MCNP_Input.py"
                          f'\n  | warning. error moving {filename}'
                          f'\n  | warning.   from {src} '
                          f'\n  | warning.   to   {dst}')


    def delete_mcnp_files(self, folder=None, extensions_to_delete=None):
        # Default args are False unless specified in command
        # NB: os.remove(f'*.r') does not work bc os.remove does not take wildcards (*)
        if not folder:
            folder = self.temp_folder

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
                    print(f"\n  __MCNP_Input.py"
                          f"\n  | comment. did not remove {f'{folder}/{file}'}"
                          f"\n  | comment. because the filepath does not exist")

    def run_mcnp(self):
        """ Runs MCNP
        """
        print(f"\n  __MCNP_Input.py")
        if self.output_filename not in os.listdir(self.outputs_folder):
            self.write_input()
            cmd = f"""mcnp6 i="{self.input_filepath}" n="{self.temp_folder}/{self.output_filename.split('.')[0]}." tasks {self.tasks}"""
            print(f"  | comment. now running mcnp:\n\n{cmd}\n\n")
            os.system(cmd)
            self.mcnp_skipped = False
        else:
            print(f'  | comment. skipping this mcnp run for {self.input_filename}'
                  f'\n  | comment.   since results already exist')
            self.mcnp_skipped = True


