import os
import sys
import shutil
import argparse

sys.path.insert(0, "./Source/")
from BaseCase import *
from Parameters import *
from Utilities import *
from ReactivityCoefficients import *
from Geometry import *
from plotStyles import *

def ReedAutomatedNeutronicsEngine(argv):
    print(" Type 'python3 HaigerlochAnalysis.py -h' for help.")

    run_types = None
    tasks = None
    cores = os.cpu_count()  # number of cores available
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
        if run_type.lower() in ['base','r']:
            run_types = ['R' if x == run_type else x for x in run_types]
        elif run_type.lower() in ['a','dens_fuel','urho','uraniumdensity']:
            run_types = ['A' if x == run_type else x for x in run_types]
        elif run_type.lower() in ['b','modr_purity','d2o',]:
            run_types = ['B' if x == run_type else x for x in run_types]
        elif run_type.lower() in ['j']:
            run_types = ['J' if x == run_type else x for x in run_types]
        elif run_type.lower() in ['sd','sphere']:
            run_types = ['SD' if x == run_type else x for x in run_types]
        else:
            print(f"\n  warning. run type '{run_type}' not recognized")
            run_types = [x for x in run_types if x != run_type]
            if len(run_types) <= 0:
                print(f"\n   fatal. no recognized run types ")
                sys.exit()

    print("\n RANE will calculate the following:")
    for run_type in run_types:
        try:
            print_desc = True
            print(f"    {RUN_DESCRIPTIONS_DICT[run_type]}")
        except:
            print_desc = False
            print(f"  warning. run type description not found")
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
        if print_desc:
            print(f"\n Currently calculating: {RUN_DESCRIPTIONS_DICT[run_type]}")

        if run_type == 'R':
            """ BASE CASE
            """

            ci = str((TANK_HEIGHT-CUBE_DIAGONAL*CUBES_A_R)/(CUBES_A_R-1))
            cube_interval = float(ci[:ci.index('.')+3]) # TRUNCATES n-1=2 digits after . place -- DO NOT ROUND!!!

            current_run = BaseCase(run_type,
                                  tasks,
                                  n_rings=N_RINGS_R,
                                  chains_per_ring=CHAINS_PER_RING_R,
                                  n_cubes_chain_a=CUBES_A_R,
                                  n_cubes_chain_b=CUBES_B_R,
                                  cube_interval=cube_interval,)
            if check_mcnp:
                print(f"\n\n================================================"
                      f"\n Running run type '{run_type}' with properties:"\
                      f"\n     tank h,r '{current_run.h_tank}', '{current_run.r_tank}'"\
                      f"\n     rings '{N_RINGS_R}', '{CUBES_TOTAL_R}' cubes"\
                      f"\n     cube interval '{cube_interval}'"\
                      f"\n     cube chain lengths '{CUBES_A_R, CUBES_B_R}'"\
                      f"\n================================================\n\n")
                current_run.run_mcnp()
                current_run.move_mcnp_files(output_types_to_move=['.o'])  # keep as separate step from run_mcnp()
            # current_run.process_rod_worth()


        elif run_type == 'radial_ex':
            """ URANIUM DENSITY
            """
            for r in RADIAL_INCREASE:
                
                tank_height = TANK_HEIGHT
                tank_radius = TANK_RADIUS + r

                ci = str((tank_height-CUBE_DIAGONAL*CUBES_A)/(CUBES_A-1))
                cube_interval = float(ci[:ci.index('.')+3]) # TRUNCATES n-1=2 digits after . place -- DO NOT ROUND!!!

                current_run = AxialGeometry(run_type,
                                      tasks,
                                      h_tank=tank_height,
                                      r_tank=tank_radius,
                                      n_rings=N_RINGS,
                                      chains_per_ring=CHAINS_PER_RING,
                                      n_cubes_chain_a=CUBES_A,
                                      n_cubes_chain_b=CUBES_B,
                                      cube_interval=cube_interval,
                                      )
                if check_mcnp:
                    print(f"\n\n================================================"
                          f"\n Running run type '{run_type}' with properties:"\
                          f"\n     tank h,r '{tank_height}', '{tank_radius}'"\
                          f"\n     rings '{N_RINGS}', '{CUBES_TOTAL}' cubes"\
                          f"\n     cube length '{CUBE_LENGTH}'"\
                          f"\n     cube interval '{cube_interval}'"\
                          f"\n     cube chain lengths '{CUBES_A,CUBES_B}'"\
                          f"\n================================================\n\n")
                    current_run.run_mcnp()
                    current_run.move_mcnp_files(output_types_to_move=['.o'])  # keep as separate step from run_mcnp()
                current_run.process_axial_keff()

        elif run_type == 'radial':
            """ URANIUM DENSITY
            """
            tank_height = TANK_HEIGHT
            tank_radius = TANK_RADIUS
            cubes_a, cubes_b = 11,10

            ci = str((tank_height-CUBE_DIAGONAL*cubes_a)/(cubes_a-1))
            cube_interval = float(ci[:ci.index('.')+3]) # TRUNCATES n-1=2 digits after . place -- DO NOT ROUND!!!

            current_run = BaseCase(run_type,
                                  tasks,
                                  h_tank=tank_height,
                                  r_tank=tank_radius,
                                  n_rings=6,
                                  chains_per_ring=[6,12,16,20,24,30],
                                  n_cubes_chain_a=cubes_a,
                                  n_cubes_chain_b=cubes_b,
                                  cube_interval=cube_interval,
                                  )
            if check_mcnp:
                print(f"\n\n================================================"
                      f"\n Running run type '{run_type}' with properties:"\
                      f"\n     tank h,r '{tank_height}', '{tank_radius}'"\
                      f"\n     cube length '{CUBE_LENGTH}'"\
                      f"\n     cube interval '{cube_interval}'"\
                      f"\n     cube chain lengths '{cubes_a,cubes_b}'"\
                      f"\n================================================\n\n")
                current_run.run_mcnp()
                current_run.move_mcnp_files(output_types_to_move=['.o'])  # keep as separate step from run_mcnp()
            current_run.process_axial_keff()


        elif run_type == 'A':
            """ URANIUM DENSITY
            """
            for fuel_density in FUEL_DENSITIES:
                current_run = DensityFuel(run_type,
                                          tasks,
                                          print_input=check_mcnp,
                                          fuel_density=fuel_density
                                          )
                if check_mcnp:
                    current_run.run_mcnp()
                    current_run.move_mcnp_files(output_types_to_move=['.o'])  # keep as separate step from run_mcnp()
                current_run.process_dens_fuel_keff()

        elif run_type == 'B':
            """ MODERATOR PURITY
            """
            for d2o_purity in MODR_PURITIES:
                current_run = Reactivity(run_type,
                                         tasks,
                                         d2o_purity=d2o_purity,
                                         )
                if check_mcnp:
                    current_run.run_mcnp()
                    current_run.move_mcnp_files()  # keep as separate step from run_mcnp()
                current_run.process_rcty_keff()
            # current_run.process_rcty_rho()  # keep outside 'for' loop-- needs all keffs before calculating rho
            # current_run.process_rcty_coef()
            # current_run.plot_rcty_coef()

        elif run_type == 'dens_grph':
            """ URANIUM DENSITY
            """
            for grph_density in GRPH_DENSITIES:
                current_run = Density(run_type,
                                       tasks,
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
                                   rod_heights={'bank': bank_height, 'ecp': ECP}, )
                if check_mcnp:
                    current_run.run_mcnp()
                    current_run.move_mcnp_files(
                        output_types_to_move=['.o', '.r', '.msht'])  # keep as separate step from run_mcnp()
                current_run.process_flux_tallies()


        elif run_type == 'axial_ex':
            """ Squeeze in as many cubes per chain into the original height, else extend tank height and decrease cube interval as minimum necessary to do so
            """
            for cube_interval in [4.2]: # CUBE_INTERVALS_EXTD[::-1]:
                packs = [11,10]
                tank_height = TANK_HEIGHT
                tank_radius = 62 # TANK_RADIUS
                chains_per_ring = [6,12,16,20,24,30]
                n_rings = len(chains_per_ring)

                if (packs[0]*(CUBE_LENGTH*np.sqrt(2)+cube_interval)-cube_interval) > TANK_HEIGHT:
                    tank_height = (packs[0]*(CUBE_LENGTH*np.sqrt(2)+cube_interval)-cube_interval)

                current_run = AxialGeometry(run_type,
                                            tasks,
                                            h_tank=tank_height,
                                            r_tank=tank_radius,
                                            n_rings=n_rings,
                                            chains_per_ring=chains_per_ring,
                                            n_cubes_chain_a=packs[0],
                                            n_cubes_chain_b=packs[1],
                                            cube_interval=cube_interval,)
                if check_mcnp:
                    print(f"\n\n================================================"
                          f"\n Running run type '{run_type}' with properties:"\
                          f"\n     tank height '{tank_height}'"\
                          f"\n     cube interval '{cube_interval}'"\
                          f"\n     cube chain lengths '{packs[0],packs[1]}'"\
                          f"\n================================================\n\n")
                    current_run.run_mcnp()
                    current_run.move_mcnp_files(output_types_to_move=['.o'])  # keep as separate step from run_mcnp()
                current_run.process_axial_keff()

        elif run_type == 'axial_z_ex_6':
            """ Squeeze in as many cubes per chain into the original height, else extend tank height and decrease cube interval as minimum necessary to do so
            """
            for cube_interval in CUBE_INTERVALS_EXTD[::-1]:
                packs = [11,10]
                tank_height = TANK_HEIGHT
                tank_radius = TANK_RADIUS

                if (packs[0]*(CUBE_LENGTH*np.sqrt(2)+cube_interval)-cube_interval) > TANK_HEIGHT:
                    tank_height = (packs[0]*(CUBE_LENGTH*np.sqrt(2)+cube_interval)-cube_interval)

                current_run = AxialGeometry(run_type,
                                            tasks,
                                            h_tank=tank_height,
                                            n_rings=6,
                                            n_cubes_chain_a=packs[0],
                                            n_cubes_chain_b=packs[1],
                                            chains_per_ring=[6,12,16,20,24,30],
                                            cube_interval=cube_interval,)
                if check_mcnp:
                    print(f"\n\n================================================"
                          f"\n Running run type '{run_type}' with properties:"\
                          f"\n     tank height '{tank_height}'"\
                          f"\n     cube interval '{cube_interval}'"\
                          f"\n     cube chain lengths '{packs[0],packs[1]}'"\
                          f"\n================================================\n\n")
                    current_run.run_mcnp()
                    current_run.move_mcnp_files(output_types_to_move=['.o'])  # keep as separate step from run_mcnp()
                current_run.process_axial_keff()

        elif run_type == 'J':
            for tank_radius in TANK_RADII_J:
                for cube_interval in CUBE_INTERVALS_J:
                    tank_height = TANK_HEIGHT
                    """ If the desired cube interval is too big, then overwrite the tank height to fit all the cubes
                    """ 
                    x = max([CUBES_A_J, CUBES_B_J])
                    if (x*(CUBE_LENGTH*np.sqrt(2)+cube_interval)-cube_interval) > TANK_HEIGHT:
                        tank_height = (x*(CUBE_LENGTH*np.sqrt(2)+cube_interval)-cube_interval)

                    """ Write input file
                    """
                    current_run = Geometry(run_type,
                                           tasks,
                                           h_tank=tank_height,
                                           r_tank=tank_radius,
                                           n_rings=N_RINGS_J,
                                           chains_per_ring=CHAINS_PER_RING_J,
                                           n_cubes_chain_a=CUBES_A_J,
                                           n_cubes_chain_b=CUBES_B_J,
                                           cube_interval=cube_interval,)

                    """ Run MCNP
                    """
                    if check_mcnp:
                        print(f"\n\n================================================"\
                              f"\n  Running Case {run_type} with properties:"\
                              f"\n    tank h, r (cm)       : {tank_height}, {tank_radius}"\
                              f"\n    number of rings      : {N_RINGS_J}"\
                              f"\n    cube interval (cm)   : {cube_interval}"\
                              f"\n    cubes per chain A, B : {CUBES_A_J}, {CUBES_B_J}"\
                              f"\n    other properties default to reference core (Case R)"\
                              f"\n================================================\n\n")
                        current_run.run_mcnp()
                        current_run.move_mcnp_files(output_types_to_move=['.o'])  
                        # keep move_mcnp_files() as separate step from run_mcnp(), else problems if Ctrl+C'ing during MCNP run
                    
                    """ Find corresponding output file, read keff, and write to csv
                    """
                    current_run.process_keff()








        elif run_type == 'pack':
            """ automatically squeeze in as many cubes per chain into the original height, or extend the tank height as minimum necessary 
            """
            for packs in CUBE_PACKS:

                tank_height = TANK_HEIGHT
                if (packs[0]*CUBE_LENGTH*np.sqrt(2)) > TANK_HEIGHT:
                    tank_height = packs[0]*CUBE_DIAGONAL

                ci = str((tank_height-CUBE_DIAGONAL*packs[0])/(packs[0]-1))
                cube_interval = float(ci[:ci.index('.')+3]) # TRUNCATES n-1=2 digits after . place -- DO NOT ROUND!!!

                current_run = AxialGeometry(run_type,
                                            tasks,
                                            h_tank=tank_height,
                                            n_cubes_chain_a=packs[0],
                                            n_cubes_chain_b=packs[1],
                                            cube_interval=cube_interval,)
                if check_mcnp:
                    print(f"\n\n================================================"
                          f"\n Running run type '{run_type}' with properties:"\
                          f"\n     tank height '{tank_height}'"\
                          f"\n     cube length '{CUBE_LENGTH}'"\
                          f"\n     cube interval '{cube_interval}'"\
                          f"\n     cube chain lengths '{packs[0],packs[1]}'"\
                          f"\n================================================\n\n")
                    current_run.run_mcnp()
                    current_run.move_mcnp_files(output_types_to_move=['.o'])  # keep as separate step from run_mcnp()
                current_run.process_axial_keff()

        elif run_type == 'plot':
            # plot the geometry and save plot figures
            if check_mcnp:
                print(f' Running geometry plotter.')
                current_run = MCNP_InputFile(run_type,
                                             tasks,
                                             template_filepath=None,
                                             rod_heights={'safe': 0, 'shim': 0, 'reg': 0},  # defaults to all rods down
                                             )
                current_run.run_geometry_plotter()
            else:
                print('\n   fatal. no plotting is available without mcnp6')
                sys.exit(2)

        elif run_type == 'axial_z':
            for cube_interval in CUBE_INTERVALS:
                current_run = AxialGeometry(run_type,
                                            tasks,
                                            cube_interval=cube_interval,)
                if check_mcnp:
                    print(" ")
                    current_run.run_mcnp()
                    current_run.move_mcnp_files(output_types_to_move=['.o'])  # keep as separate step from run_mcnp()
                current_run.process_axial_keff()

        elif run_type == 'rcty_modr':
            """ MODERATOR TEMPERATURE COEFFICIENT
            """
            for d2o_temp_C in D2O_MOD_TEMPS_C:
                current_run = Reactivity(run_type,
                                         tasks,
                                         d2o_temp_K=float(d2o_temp_C + 273),
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

        elif run_type == 'void':
            if check_mcnp:
                current_run = MCNP_InputFile(run_type,
                                             tasks,
                                             template_filepath=None,
                                             rod_heights=rod_heights_dict,
                                             h2o_temp_K=h2o_temp_K,
                                             h2o_density=h2o_density,
                                             rcty_type=rcty_type,
                                             ct_cell_mat=101,
                                             ct_mat_density=0.001225  # g/cc
                                             )
                current_run.run_mcnp()


if __name__ == "__main__":
    ReedAutomatedNeutronicsEngine(sys.argv[1:])