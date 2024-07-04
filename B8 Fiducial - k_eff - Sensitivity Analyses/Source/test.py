import numpy as np
h_tank = 119.8
n_cubes_chain_a = 12
CUBE_DIAGONAL = 3.97*np.sqrt(2)
c = (h_tank-CUBE_DIAGONAL*n_cubes_chain_a)/(n_cubes_chain_a-1)
ci = str((h_tank-CUBE_DIAGONAL*n_cubes_chain_a)/(n_cubes_chain_a-1))
cube_interval = float(ci[:ci.index('.')+3]) # TRUNCATES n-1=2 digits after . place -- DO NOT ROUND!!!
first_cube_offset = float('{:.2f}'.format((h_tank - (n_cubes_chain_a*CUBE_DIAGONAL+(n_cubes_chain_a-1)*cube_interval))/2))
print(ci, cube_interval,first_cube_offset)
