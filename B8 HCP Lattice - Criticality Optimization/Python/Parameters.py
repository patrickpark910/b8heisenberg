import numpy as np


""" MCNP Settings
"""
N_PER_CYCLE = 200000
DISCARD_CYCLES = 10
TOTAL_CYCLES = 80
INPUT_TEMPLATE_FILEPATH = f"./Python/b8hcp.template"


""" Run type SC
"""
SC_N_CUBES = [1300,1312,1325,1337,1350,1362,1375,1387,1400,1412,1425,1437,1450,1462,1475,1487,1500,1525,1550,1575,1600,1625,1650,1675,1700,1725,1750,1775,1800] # 500,550,600,664,700,750,800,850,900,1000,1100,1150,1200,1250, ,2000,2100,2200,
SC_MODR_VOLS = [1200e3,1400e3,1800e3,2000e3,2200e3,2600e3,3000e3,3400e3,3800e3,4200e3] # cc # 1800e3,2200e3,2600e3,3000e3,3400e3,
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

