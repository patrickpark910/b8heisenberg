import numpy as np
RUN_DESCRIPTIONS_DICT = {'base':'base case, original haigerloch core',
						 'dens_fuel':'variation of fuel density'}
CUBE_LENGTH = 5
CUBE_DIAGONAL = CUBE_LENGTH * np.sqrt(2)
FUEL_DENSITIES = [18.00,18.05,18.10,18.15,18.20,18.25,18.30,18.35,18.40,18.45,18.50,18.55,18.60,18.65,18.70,18.75,18.80,18.85,18.90,18.95,19.00,19.05,19.10,19.15,19.20,19.25,19.30] #g/cc
D2O_MOD_TEMPS_C = [1,5,10,15,20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 99] # MUST HAVE differences of >=1 or else input file naming will fail
D2O_MOD_PURITIES = [85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100]