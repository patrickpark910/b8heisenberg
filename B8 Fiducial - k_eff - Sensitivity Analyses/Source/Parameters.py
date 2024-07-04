import numpy as np


CUBES_A, CUBES_B = 11, 10  # 9, 8  
N_RINGS, CHAINS_PER_RING = 6, [6,12,16,20,24,30] # 5, [6,12,16,20,24]

RADIAL_INCREASE = [27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45] # [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,

FUEL_DENSITIES = [15.00,15.25,15.50,15.75,16.00,16.25,16.50,16.75,17.00,17.25,17.50,17.75,18.00,18.25,18.50,18.75,19.0,19.25] #g/cc
D2O_MOD_TEMPS_C = [1,5,10,15,20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 99] # MUST HAVE differences of >=1 or else input file naming will fail
CUBE_INTERVALS = [0,0.5,1.0,1.5,2.0,2.5,3.0,3.5,4.0,4.5,5.0,5.5,6.0,6.5,7.0] # file naming convention only allows up to 2 decimals
CUBE_INTERVALS_EXTD = [6.0,6.5,7.0,7.5,8.0,8.5,9.0,9.5,10.0,] #10.5,11.0,11.5,12.0,12.5,]#,[5.5,11.5,12.0,12.5,13.0,13.5,14.0,14.5,15.0]
CUBE_PACKS = [[9,8],[10,9],[11,10],[12,11],[13,12],[14,13],[15,14],[16,15],[17,16],[18,16]]

""" Case B
"""
MODR_PURITIES = [85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100]


""" Case J 
NB. Input file naming only allows: 
        integer tank heights and radii
        up to hundreths (0.01) float for cube intervals
"""
CUBES_A_J, CUBES_B_J = 9, 8 # 11, 10
N_RINGS_J, CHAINS_PER_RING_J = 5, [6,12,16,20,24] # 6, [6,12,16,20,24,30]
TANK_RADII_J = [82,84,86] # list [61.7,64,66,68,70,72,74,76,78,80,
CUBE_INTERVALS_J = [5.5,6.0,6.5,7.0,7.5,8.0,8.5,9.0,9.5,10.0, 10.5,11.0,11.5,12.0,12.5,13.0,13.5,14.0,14.5,15.0,15.5,16.0,16.5,17.0] # list


""" MCNP Settings
"""
N_PER_CYCLE = 200000
DISCARD_CYCLES = 15
KCODE_CYCLES = 115

#
#
# probably don't need to change these unless you really understand the code

""" Reference settings
"""
TANK_HEIGHT = 124 # 124
TANK_RADIUS = 61.7 # 61.7
FUEL_DENSITY = 18.5349 # g/cc
GRPH_DENSITY_TOP = 1.58 # g/cc
GRPH_DENSITY_BOT = 1.58 # g/cc
GRPH_DENSITY_SIDE = 1.70 # g/cc
D2O_PURITY = 96.8 # 99.6 # 96.8 at%
AMBIENT_TEMP_K = 284 # Atomkeller Museum confirmed 10 C less than outside so 21 C room temp --> 11 C.
CUBES_A_R, CUBES_B_R = 9, 8 # 11, 10
N_RINGS_R, CHAINS_PER_RING_R = 5, [6,12,16,20,24] # 6, [6,12,16,20,24,30]

RUN_DESCRIPTIONS_DICT = {'base':'base case, original haigerloch core',
			'A':'vary fuel density',
			'axial_z':'vertical cube interval'}

CUBE_LENGTH = 5.0 # round((5**3*1)**0.33333,4) # N% volume of 5cm
CUBE_DIAGONAL = CUBE_LENGTH * np.sqrt(2)

CUBES_TOTAL_R = int(0)
for chains_per_ring in CHAINS_PER_RING_R:
	if chains_per_ring % 2 == 0: # even
		cubes_subtotal = chains_per_ring/2*(CUBES_A_R+CUBES_B_R)
	else:
		cubes_subtotal = (chains_per_ring-1)/2*(CUBES_A_R+CUBES_B_R) + CUBES_A_R
	CUBES_TOTAL_R += int(cubes_subtotal)