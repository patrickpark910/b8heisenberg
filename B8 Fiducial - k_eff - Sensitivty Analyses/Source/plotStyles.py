import matplotlib.pyplot as plt
import numpy as np
from Parameters import *



# figure settings
FIGSIZE = (1636/96, 3*673/96)
LINEWIDTH = 2.5
SMALL_SIZE = 14
MEDIUM_SIZE = 18
LARGE_SIZE = 22
HUGE_SIZE = 28
LINE_COLORS = {'safe':'tab:red', 'shim':'tab:green', 'reg':'tab:blue', 'bank':'tab:purple', 
                'rcty_fuel':'tab:red', 'rcty_void':'tab:green', 'rcty_modr': 'tab:blue'}
LINE_STYLES =  {'safe': '-', 'shim':'--', 'reg':':', 'bank':'-',
                'rcty_fuel':'-', 'rcty_void':'-', 'rcty_modr':'-'}
# linestyle = ['-': solid, '--': dashed, '-.' dashdot, ':': dot]
MARKER_STYLES = {'safe': 'o', 'shim':'^', 'reg':'s', 'bank':'o',
                     'rcty_fuel':'o', 'rcty_void':'o', 'rcty_modr':'o'}
MARKER_SIZE = 8 # default marker sizes: 6
plt.rc('font', size=MEDIUM_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=LARGE_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=MEDIUM_SIZE)    # legend fontsize
plt.rc('figure', titlesize=LARGE_SIZE)  # fontsize of the figure title