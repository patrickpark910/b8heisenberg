import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

# Read the big CSV file
df = pd.read_csv('flux_hwtr_fuel_csv.csv')

# Create a figure and axis
fig, ax = plt.subplots(figsize=(4, 3))

ax.plot(df.iloc[:, 1], df.iloc[:, 2], 
        label='th', linewidth=1, color="red", # marker='+'
       ) # 

# Add labels and legend
# Set the font size for various elements
# ax.set_xlim(left=0)
# ax.set_xlim(right=40)
# ax.set_ylim(bottom=0)

ax.set_xscale('log')
ax.set_yscale('linear')
ax.set_xticks([1e-2,1e0,1e2,1e4,1e6,]) # 1e-1,1e1,1e3,1e5,1e7
ax.set_yticks([1e-5,1e-6])
ax.set_xlim(0, 2e7)
ax.set_ylim(0, 1.75e-5)

# Add labels and legend
ax.set_xlabel('Neutron Energy [eV]', fontname='Arial')
ax.set_ylabel(r'Flux [n/cm$^2$/s] per Source Neutron', fontname='Arial')

# Set the font of the tick labels to Arial
for tick in ax.get_xticklabels() + ax.get_yticklabels():
    tick.set_fontname('Arial')
plt.rcParams.update({'font.size': 36})

# ax.legend(prop={'family': 'Arial'})

# Display the plot
plt.savefig("test.svg", transparent=True, bbox_inches='tight',pad_inches=0, format="svg")
plt.show()