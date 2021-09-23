import os
import sys
import shutil
import argparse

sys.path.insert(0, "./Source/")
from BaseCase import *
from Parameters import *
from Utilities import *

"""
This file uses PEP8 Python Style Guidelines.
Constants are in CAPS and are most likely defined in ./Python/Parameters.py
The structure of this Python file is based on a similar engine for the
National Institute of Standards and Technology, written by Dr. Danyal Turkoglu,
with whom I worked with in May-November 2020.
"""


def ReedAutomatedNeutronicsEngine(argv):
    # print(" Type 'python3 NeutronicsEngine.py -h' for help.")
    print(" Type 'python3 HaigerlochAnalysis.py -h' for help.")

    run_types = None
    tasks = None
    cores = os.cpu_count()  # number of cores available
    core_number = 49  # refers to reactor core number
    check_mcnp = True
    if shutil.which('mcnp6') is None:
        print(" MCNP6 is not available on this device.")
        check_mcnp = False

    """
    Argument parsing setup
    Returns args_dict, a dictionary of arguments and their options,
    ex: args_dict = {'r': 1, 't': 12, 'm': 1}
    ex: args_dict = {'r': 1, 't': None, 'm': 1}
    with 'None' if no option is selected for that argument and a default is 
    not specified in the add_argument.
    """
    parser = argparse.ArgumentParser(description=' Description of your program')
    parser.add_argument('-r',
                        help=" R = g \n h \n c")
    parser.add_argument('-t',
                        help=f" T = integer from 1 to {cores}. Number of CPU cores to be used for MCNP.")
    parser.add_argument('-m',
                        help=' M = 1: run mcnp, 0: do not run mcnp (default: 1)',
                        default=check_mcnp)
    args_dict = vars(parser.parse_args())
    print(os.getcwd())

    """
    Argument parsing
    """
    # -r
    if args_dict['r'] is None:
        print("   Fatal. No run types selected.")
        sys.exit()

    run_types = list(args_dict['r'].split(','))
    for run_type in run_types:
        if run_type.lower() in ['b','base']:
            run_types = ['base' if x == run_type else x for x in run_types]
        elif run_type.lower() in ['dens_fuel','urho','uraniumdensity']:
            run_types = ['dens_fuel' if x == run_type else x for x in run_types]
        else:
            print(f"\n  warning. run type '{run_type}' not recognized")
            run_types = [x for x in run_types if x != run_type]
            if len(run_types) <= 0:
                print(f"\n   fatal. no recognized run types ")
                sys.exit()

    print("\n RANE will calculate the following:")
    for run_type in run_types:
        print(f"    {RUN_DESCRIPTIONS_DICT[run_type]}")
    proceed = None
    while proceed is None:
        proceed = input(f"\n Proceed (Y/N)? ")
        if proceed.lower() == "y":
            pass
        elif proceed.lower() == "n":
            sys.exit()
        else:
            proceed = None

    # -t
    if isinstance(args_dict['t'], int) and int(args_dict['t']) <= cores:
        pass
    else:
        print("\n No <tasks> specified, or invalid <tasks> in '-t <tasks>'.")
        tasks = get_tasks()  # Utilities.py

    # -m
    if args_dict['m'] in [1, '1', 't', 'T', "true", "True"] and shutil.which('mcnp6') is None:
        print("\n  Warning. You have specified to run MCNP6, but MCNP6 is not available on this device.")
        check_mcnp = False
    elif args_dict['m'] in [0, '0', 'f', 'F', "false", "False"]:
        print("\n  Warning. You have specified to not run MCNP6. Data will be processed from existing output files.")
        check_mcnp = False
    else:
        check_mcnp = True

    """
    Make sure the right directories exist
    """
    for folder in ["MCNP", "Results"]:
        if not os.path.exists('./' + folder): os.mkdir(folder)

    """
    Execute run types
    """
    rane_cwd = os.getcwd()

    for run_type in run_types:
        print(f"\n Currently calculating: {RUN_DESCRIPTIONS_DICT[run_type]}")

        if run_type == 'base':
            """ BASE CASE
            """
            current_run = BaseCase(run_type,
                                  tasks,
                                  core_number=core_number,
                                  )
            if check_mcnp:
                current_run.run_mcnp()
                current_run.move_mcnp_files(output_types_to_move=['.o'])  # keep as separate step from run_mcnp()
            # current_run.process_rod_worth()


        elif run_type == 'crit':
            """ CRITICAL LOADING EXPERIMENT
            """
            pass
            fuel_to_remove = []
            while len(fuel_to_remove) == 0:
                user_input = input(
                    f"Input core positions separated by a comma (ex: C1,C2,E4,F1), 'sop' to input the standard procedure for the 1/M experiment ({FUEL_REMOVED_SOP}), or 'quit' to quit: ")
                if user_input.lower() in ['s', 'sop']:
                    user_input = FUEL_REMOVED_SOP
                elif user_input.lower() in ['q', 'quit', 'kill']:
                    sys.exit()

                user_input = user_input.split(',')
                for c in user_input:
                    if c.upper() in CORE_POS:
                        fuel_to_remove.append(c)  # user_input is matched with a FE
                    else:
                        print(f"\n  Warning. There is no fuel element in core position {c}.")

            CriticalLoading(rane_cwd, base_file_path=base_file_name, check_mcnp=check_mcnp, tasks=tasks,
                            fuel_to_remove=fuel_to_remove)


        elif run_type == 'dens_fuel':
            """ URANIUM DENSITY
            """
            for fuel_density in FUEL_DENSITIES:
                current_run = DensityFuel(run_type,
                                          tasks,
                                          core_number=core_number,
                                          print_input=check_mcnp,
                                          fuel_density=fuel_density
                                          )
                if check_mcnp:
                    current_run.run_mcnp()
                    current_run.move_mcnp_files(output_types_to_move=['.o'])  # keep as separate step from run_mcnp()
                current_run.process_dens_fuel_keff()

        elif run_type == 'dens_grph':
            """ URANIUM DENSITY
            """
            for grph_density in GRPH_DENSITIES:
                current_run = Density(run_type,
                                       tasks,
                                       core_number=core_number,
                                       print_input=check_mcnp,
                                       )
                if check_mcnp:
                    current_run.run_mcnp()
                    current_run.move_mcnp_files(output_types_to_move=['.o'])  # keep as separate step from run_mcnp()
                current_run.process_keff()

        elif run_type == 'flux':
            """ FLUXES - calculate fluxes at ir positions and control rods
                uses kopts card in mcnp6, needs to be as close to keff=1 as possible for best results (MCNP6.2 manual 3-168)
            """
            for bank_height in BANK_HEIGHTS_FLUX + [ECP]:
                current_run = Flux(run_type,
                                   tasks,
                                   core_number=core_number,
                                   rod_heights={'bank': bank_height, 'ecp': ECP}, )
                if check_mcnp:
                    current_run.run_mcnp()
                    current_run.move_mcnp_files(
                        output_types_to_move=['.o', '.r', '.msht'])  # keep as separate step from run_mcnp()
                current_run.process_flux_tallies()

        elif run_type == 'plot':
            # plot the geometry and save plot figures
            if check_mcnp:
                print(f' Running geometry plotter.')
                current_run = MCNP_InputFile(run_type,
                                             tasks,
                                             template_filepath=None,
                                             core_number=core_number,
                                             rod_heights={'safe': 0, 'shim': 0, 'reg': 0},  # defaults to all rods down
                                             )
                current_run.run_geometry_plotter()
            else:
                print('\n   fatal. no plotting is available without mcnp6')
                sys.exit(2)

        elif run_type == 'powr':
            pass

        elif run_type == 'rcty_modr':
            """ MODERATOR TEMPERATURE COEFFICIENT
            """
            for h2o_temp_C in H2O_MOD_TEMPS_C:
                current_run = Reactivity(run_type,
                                         tasks,
                                         template_filepath=None,
                                         core_number=core_number,
                                         rod_heights={'bank': 100},  # ECP},
                                         h2o_temp_K=float(h2o_temp_C + 273),
                                         )
                if check_mcnp:
                    current_run.run_mcnp()
                    current_run.move_mcnp_files(output_types_to_move=['.o'])  # keep as separate step from run_mcnp()
                current_run.process_rcty_keff()
            current_run.process_rcty_rho()  # keep outside 'for' loop-- needs all keffs before calculating rho
            current_run.process_rcty_coef()
            current_run.plot_rcty_coef()

        elif run_type == 'rcty_fuel':
            """ FUEL TEMPERATURE COEFFICIENT
            """
            for u235_temp_K in UZRH_FUEL_TEMPS_K:
                current_run = Reactivity(run_type,
                                         tasks,
                                         template_filepath=None,
                                         core_number=core_number,
                                         rod_heights={'bank': 100},  # ECP},
                                         uzrh_temp_K=u235_temp_K,
                                         )
                if check_mcnp:
                    current_run.run_mcnp()
                    current_run.move_mcnp_files()  # keep as separate step from run_mcnp()
                current_run.process_rcty_keff()
            current_run.process_rcty_rho()  # keep outside 'for' loop-- needs all keffs before calculating rho
            current_run.process_rcty_coef()
            current_run.plot_rcty_coef()

        elif run_type == 'rcty_void':
            """ VOID COEFFICIENT (MODERATOR)
            """
            for h2o_void_percent in H2O_VOID_PERCENTS:
                current_run = Reactivity(run_type,
                                         tasks,
                                         print_input=True,
                                         template_filepath=None,
                                         core_number=core_number,
                                         rod_heights={'bank': 100},  # ECP},
                                         h2o_void_percent=h2o_void_percent,
                                         )
                if check_mcnp:
                    current_run.run_mcnp()
                    current_run.move_mcnp_files()  # keep as separate step from run_mcnp()
                current_run.process_rcty_keff()
            current_run.process_rcty_rho()  # keep outside 'for' loop-- needs all keffs before calculating rho
            current_run.process_rcty_coef()
            current_run.plot_rcty_coef()

        elif run_type == 'void':
            if check_mcnp:
                current_run = MCNP_InputFile(run_type,
                                             tasks,
                                             template_filepath=None,
                                             core_number=core_number,
                                             rod_heights=rod_heights_dict,
                                             h2o_temp_K=h2o_temp_K,
                                             h2o_density=h2o_density,
                                             rcty_type=rcty_type,
                                             ct_cell_mat=101,
                                             ct_mat_density=0.001225  # g/cc
                                             )
                current_run.run_mcnp()

        elif run_type == 'rodcal':
            # calibrate individual rods
            for rod in RODS:
                for rod_height in ROD_CAL_HEIGHTS:
                    rod_heights_dict = {'bank': 100}
                    if rod == 'reg':
                        rod_heights_dict = {'bank': 80}  # 80}
                    rod_heights_dict[rod] = rod_height

                    current_run = RodCalibration(run_type,
                                                 tasks,
                                                 template_filepath=None,
                                                 core_number=core_number,
                                                 rod_heights=rod_heights_dict,
                                                 rod_config_id=rod,
                                                 add_samarium=True,
                                                 )
                    if check_mcnp:
                        current_run.run_mcnp()
                        current_run.move_mcnp_files(output_types_to_move=['.o'])
                    current_run.extract_keff()
                    current_run.process_rod_worth()
            current_run.process_rod_params()
            current_run.plot_rod_worth()

        elif run_type == 'sdm':
            # calculate shutdown margins with various stuck rods
            for sdm_config_id in list(SDM_CONFIGS_DICT.keys()):
                rod_heights_dict = SDM_CONFIGS_DICT[sdm_config_id]
                current_run = ShutdownMargin(run_type,
                                             tasks,
                                             rod_heights=rod_heights_dict,
                                             rod_config_id=sdm_config_id,
                                             )
                if check_mcnp:
                    current_run.run_mcnp()
                    current_run.move_mcnp_files()
                current_run.extract_keff()
                current_run.process_sdm()


if __name__ == "__main__":
    ReedAutomatedNeutronicsEngine(sys.argv[1:])