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
xi = np.linspace(c.min(), c.max(), 100)
yi = np.linspace(m.min(), m.max(), 100)
X, Y = np.meshgrid(xi, yi)
Z = griddata((c, m), k, (X, Y), method='cubic')


# Plot with filled contours, contour lines, and labels at each 0.01 increment
z_min, z_max = np.nanmin(Z), np.nanmax(Z)

plt.rc('font', family='Arial', size=12)

plt.figure(figsize=(10, 8))

original_cmap = plt.get_cmap('coolwarm')
truncated_cmap = truncate_colormap(original_cmap, minval=0.275, maxval=1.0).with_extremes(under="#8db0fe")

# cmap = plt.colormaps['coolwarm'].with_extremes(under="#3b4cc0") # coolwarm = ['#3b4cc0', '#8db0fe', '#dddddd', '#f49a7b', '#b40426']
levels = np.linspace(.9, 1.02, num=13) # [.91,.92,.93,0.94,0.95,.96,.97,.98,.99,1.00,1.01]
contour_filled = plt.contourf(X, Y, Z, levels=levels, cmap=truncated_cmap, extend="min")
contour_lines = plt.contour(X, Y, Z, levels=levels, colors='black', linewidths=0.5)
plt.colorbar(contour_filled, label='Effective multiplication [k-eff]')
plt.clabel(contour_lines, inline=True, fontsize=11, fmt='%1.2f')

plt.scatter(c, m)

plt.xticks(np.arange(500, 1500, step=100)) 
plt.yticks(np.arange(1200, 4200, step=400)) 

plt.xlabel('Number of cubes', family='Arial', fontsize=12)
plt.ylabel('Moderator volume [L]', family='Arial', fontsize=12)
# plt.title('')
plt.show()


