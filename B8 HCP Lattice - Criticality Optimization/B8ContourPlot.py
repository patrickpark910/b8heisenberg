import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from scipy.interpolate import griddata

def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    new_cmap = mcolors.LinearSegmentedColormap.from_list(
        f'trunc({cmap.name},{minval:.2f},{maxval:.2f})',
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap


# Load the CSV file
data = pd.read_csv('./Results/SC/b8hcp-caseSC-keff.csv')
c, m, k = data['cubes'], data['modr v L'], data['keff']

# Create a grid to interpolate the data
xi = np.linspace(c.min(), c.max(), 1000)
yi = np.linspace(m.min(), m.max(), 1000)
X, Y = np.meshgrid(xi, yi)
Z = griddata((c, m), round(k,3), (X, Y), method='cubic') # nearest, cubic


# Plot with filled contours, contour lines, and labels at each 0.01 increment
z_min, z_max = np.nanmin(Z), np.nanmax(Z)
FONTSIZE = 15

plt.rc('font', family='Arial', size=FONTSIZE)
plt.figure(figsize=(16, 8))

original_cmap = plt.get_cmap('coolwarm')
truncated_cmap = truncate_colormap(original_cmap, minval=0.275, maxval=1.0).with_extremes(under="#8db0fe")

# cmap = plt.colormaps['coolwarm'].with_extremes(under="#3b4cc0") # coolwarm = ['#3b4cc0', '#8db0fe', '#dddddd', '#f49a7b', '#b40426']
levels = np.linspace(.9, 1.02, num=13) # [.91,.92,.93,0.94,0.95,.96,.97,.98,.99,1.00,1.01]
contour_filled = plt.contourf(X, Y, Z, levels=levels, cmap=truncated_cmap, extend="min")
contour_lines = plt.contour(X, Y, Z, levels=levels, colors='black', linewidths=0.5)
cbar = plt.colorbar(contour_filled,)

# plt.grid(which='minor', linestyle='-', linewidth=0.5, color='black',alpha=0.33)
plt.grid(which='major', linestyle='-', linewidth=0.5, color='black',alpha=0.5)

plt.clabel(contour_lines, inline=True, fontsize=FONTSIZE, fmt='%1.2f')
cbar.set_label('Effective multiplication [k-eff]', fontsize=FONTSIZE)

plt.scatter(c, m) # turns on the dots
plt.minorticks_on()
plt.xticks(np.arange(500, 2300, step=200)) 
plt.yticks(np.arange(1200, 4200, step=400)) 


plt.xlabel('Number of nU cubes', family='Arial', fontsize=FONTSIZE)
plt.ylabel('96.8%-pure heavy water volume [L]', family='Arial', fontsize=FONTSIZE)

# plt.savefig('b8-contour-highres.svg', dpi=500, bbox_inches='tight', pad_inches=0)
# plt.savefig('b8-contour-highres.png', dpi=500, bbox_inches='tight', pad_inches=0)
plt.show()


