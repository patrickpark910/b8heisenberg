import os
import sys
import shutil
import argparse

sys.path.insert(0, "./Python/")
from MCNP_Input import *
from Parameters import *
from Utilities import *
from MCNP_Output import *


def B8Cylinder(argv):
    # print(" Type 'python3 NeutronicsEngine.py -h' for help.")
    print(" Type 'python3 B8Optimize.py -h' for help.")

    run_types, tasks, cores, check_mcnp = None, None, os.cpu_count(), True
    if shutil.which('mcnp6') is None:
        print(" MCNP6 is not available on this device.")
        check_mcnp = False

    """ Argument parsing setup
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
    print(f" Current working directory: {os.getcwd()}")


    """ Argument parsing (-r)
    """
    if args_dict['r'] is None:
        print("  fatal. No run types selected.")
        sys.exit()

    run_types = list(args_dict['r'].split(','))
    for run_type in run_types:
        if run_type.lower() in ['base','r','sr']:
            run_types = ['SR' if x == run_type else x for x in run_types]
        elif run_type.lower() in ['sc']:
            run_types = ['SC' if x == run_type else x for x in run_types]
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

    # Argument parsing (-t) 
    try:
        if int(args_dict['t']) <= cores:
            tasks = int(args_dict['t'])
            print(f"  Running with {args_dict['t']} tasks.")
        else: 
            raise ValueError
    except:
        print("\n No <tasks> specified, or invalid <tasks> in '-t <tasks>'.")
        tasks = get_tasks()  # Utilities.py

    # Argument parsing (-m)
    if args_dict['m'] in [1, '1', 't', 'T', "true", "True"] and shutil.which('mcnp6') is None:
        print("\n  Warning. You have specified to run MCNP6, but MCNP6 is not available on this device.")
        check_mcnp = False
    elif args_dict['m'] in [0, '0', 'f', 'F', "false", "False"]:
        print("\n  Warning. You have specified to not run MCNP6. Data will be processed from existing output files.")
        check_mcnp = False
    else:
        check_mcnp = True


    """ Make sure the right directories exist
    """
    for folder in ["MCNP", "Results"]:
        if not os.path.exists('./' + folder): os.mkdir(folder)


    """ Execute run types
    """
    rane_cwd = os.getcwd()
    for run_type in run_types:
        if print_desc:
            print(f"\n Currently calculating: {RUN_DESCRIPTIONS_DICT[run_type]}")
        
        print(f"")
        if run_type == 'SC':
            fails, failed_files, stop_stop_its_already_dead = 0, [], 1
            for n in reversed(SC_N_CUBES): # SD_N_CUBES:
                for m in reversed(SC_MODR_VOLS):
                    if fails < stop_stop_its_already_dead:
                        print(f"\n\n================================================" 
                           f"\n  __B8Optimize.py"
                           f"\n  | Processing run type '{run_type}' with properties:"\
                           f"\n  |   core radius [cm] : {rd(((n*CUBE_LENGTH**3 + m)/2/np.pi)**(1/3),4)}"
                           f"\n  |   n cubes          : {n}"
                           f"\n  |   modr vol [L]     : {m/1e3} " ) # 
                        #   f"\n================================================")
                        current_run = Cylinder(run_type,
                                               tasks,
                                               n_cubes  = n,            # nominal = 664
                                               modr_vol = m,)

                        if check_mcnp:
                            current_run.run_mcnp()
                            current_run.move_mcnp_files(output_types_to_move=['.o'])  # keep as separate step from run_mcnp()
                        else: 
                            current_run.mcnp_skipped = True  
                        
                        try:
                            current_run.process_keff()
                        except:
                            print(f"\n  __B8Optimize.py"
                               f"\n  | warning.  k-eff not found in {current_run.output_filepath}"\
                               f"\n  | warning.  check if mcnp input was written correctly"\
                               f"\n================================================\n\n")
                            fails += 1
                            failed_files.append(current_run.input_filename)
                    else:
                        continue
            if fails > 0:
                print(f"\n\n================================================" 
                      f"\n  __B8Optimize.py\n")
                if fails == stop_stop_its_already_dead:
                    print(f"  | fatal.    B8Optimize.py auto-terminated because {fails} inputs failed to produce a k-eff")
                    print(f"  | fatal.    max allowed fails set to {stop_stop_its_already_dead}\n")
                print(f"  | warning.  errors in at least {fails} input files")
                print(f"  | warning.  check if these mcnp inputs were written correctly in:")
                print(f"  | warning.  {current_run.inputs_folder}/")
                for f in failed_files:
                    print(f"  | warning.    {f}")   
                print(f"\n================================================\n\n")



if __name__ == "__main__":
    B8Cylinder(sys.argv[1:])