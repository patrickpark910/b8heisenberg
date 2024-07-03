import numpy as np


""" MCNP Settings
"""
N_PER_CYCLE = 200000
DISCARD_CYCLES = 10
TOTAL_CYCLES = 80
INPUT_TEMPLATE_FILEPATH = f"./Python/b8hcp.template"


""" Run type SC
"""
SC_N_CUBES = [500,600,664,700,800,900,1100,1200,1300,1400,1500,850,1600,1650,1000,1700,1800,1900,2000,2100,2200] # 550, 750, 850, 550, 650,750,1150,1250,1350,1450,1550,
SC_MODR_VOLS = [1200e3,1400e3,1800e3,2200e3,2600e3,3000e3,3400e3,3800e3,4200e3] # cc # 1800e3,2200e3,2600e3,3000e3,3400e3,
# probably don't need to change these unless you really understand the code

""" B8 Reference settings 
definitely do not change this unless you know exactly what you're doing
"""
N_CUBES = 664
CUBE_LENGTH = 5.0
CORE_RADIUS = 61.7 # 61.7
FUEL_DENSITY = 18.5349 # g/cc
GRPH_DENSITY = 1.58 # g/cc
D2O_PURITY = 96.8 # mol%
AMBIENT_TEMP_K = 284 # Atomkeller Museum confirmed 10 C less than outside so 21 C room temp --> 11 C.
MODR_VOL = 1400e3
GRPH_VOL = (np.pi*(210.8/2)**2*216.0)-(np.pi*(123.4/2)**2*124.0)

RUN_DESCRIPTIONS_DICT = {'base':'base case, original haigerloch core',
						 'SD':'hcp lattice in sphere',
						 'SC':'hcp lattice in cylinder'}

