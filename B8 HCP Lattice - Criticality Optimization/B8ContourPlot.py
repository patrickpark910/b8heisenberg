import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter


def main():

    # Load the CSV file
    data = pd.read_csv('./Results/SC/b8hcp-caseSC-keff.csv')
    c = data['cubes'].to_numpy()
    m = data['modr v L'].to_numpy()
    k = data['keff'].to_numpy()

    # Build interpolation grid
    xi = np.linspace(c.min(), c.max(), 500) # GRID_N = 500 : grid resolution per axis (< 1000 for speed; increase if needed)
    yi = np.linspace(m.min(), m.max(), 500)
    X, Y = np.meshgrid(xi, yi)

    # Interpolant. Use linear to avoid ringing (which you can get in cubic)
    Z_lin = griddata((c, m), k, (X, Y), method='cubic') # linear, cubic

    # Smooth with Gaussian filter
    Z = gaussian_filter_nan(Z_lin, sigma=3) # sigma: Gaussian blur strength in grid cells; use 1.5-3 for gentle smoothing



    """
    PLOTTING
    """
    
    LEVELS = np.linspace(0.90, 1.02, num=13)
    FONTSIZE = 15

    # Plot
    plt.rc('font', family='Arial', size=FONTSIZE)
    fig, ax = plt.subplots(figsize=(16, 10))

    original_cmap = plt.get_cmap('coolwarm')
    truncated_cmap = truncate_colormap(original_cmap, minval=0.275, maxval=1.0)
    truncated_cmap.set_under("#8db0fe")
    print(f"Matplotlib version: {matplotlib.__version__}")  # 👈 inline version print


    contour_filled = ax.contourf(X, Y, Z, levels=LEVELS, cmap=truncated_cmap, extend="min")
    contour_lines  = ax.contour(X, Y, Z, levels=LEVELS, colors='black', linewidths=0.5)


    # Increase space between the main axes (incl. right y-axis) and the colorbar
    cbar = fig.colorbar(contour_filled, ax=ax, pad=0.12, fraction=0.035) 
    ax.clabel(contour_lines, inline=True, fontsize=FONTSIZE, fmt='%1.2f')

    ax.grid(which='major', linestyle='-', linewidth=0.5, color='black', alpha=0.5)
    ax.scatter(c, m, s=12, color='k', alpha=0.35, zorder=3)  # keep points, but deemphasize

    # Primary axes
    ax.set_xlabel(r'Number of uranium cubes', fontsize=FONTSIZE)
    ax.set_ylabel('96.8%-pure heavy water volume [L]', fontsize=FONTSIZE)
    cbar.set_label('Effective multiplication [k-eff]', fontsize=FONTSIZE)

    ax.minorticks_on()
    ax.set_xticks(np.arange(500, 2300, step=200))
    ax.set_yticks(np.arange(1200, 4200, step=400))

    ax.set_xlim(500, 2200)
    ax.set_ylim(1200, 4200)

    # Secondary axes
    # Right y: liters -> kg 
    secax_y = ax.secondary_yaxis('right', functions=(liters_to_kg, kg_to_liters))
    secax_y.set_ylabel(r'96.8%-pure heavy water mass [kg] (1.11 g/cm$^3$)', fontsize=FONTSIZE)
    secax_y.tick_params(axis='y', pad=8)  # <-- add tick padding

    # Top x: number of cubes -> kg 
    secax_x = ax.secondary_xaxis('top', functions=(cubes_to_kg, kg_to_cubes))
    secax_x.tick_params(axis='x', pad=6)  # space between ticks and label
    secax_x.set_xlabel(r'Uranium mass [kg] (18.53 g/cm$^3$)', fontsize=FONTSIZE)


    # Dotted line for optimal V_M/V_F ratio = V_D2O / V_U = 18.6
    x_line = np.linspace(c.min(), c.max(), 500)
    y_line = 18.6 * CUBE_VOL_L * x_line
    ax.plot(x_line, y_line, linestyle=':', linewidth=2, color='k')

    # Optional label in axes coordinates
    #ax.text(0.02, 0.96, r'$V_{\mathrm{D_2O}}/V_{\mathrm{U}} = 18.6$',
    #        transform=ax.transAxes, ha='left', va='top', fontsize=FONTSIZE-2,
    #        bbox=dict(facecolor='white', alpha=0.6, edgecolor='none', pad=2))

    """
    Extract k-eff = 1.00 contour 
    """
    k_1_contour = ax.contour(X, Y, Z, levels=[1.00], colors='red', linewidths=2, alpha=0.8)

    # Extract the path vertices of the k-eff = 1.00 contour line
    path = k_1_contour.get_paths()[0]
    vertices = path.vertices
    x_contour = vertices[:, 0]
    y_contour = vertices[:, 1]
    
    # Find minimum x point on the contour
    min_x_idx = np.argmin(x_contour)
    min_x_point = (x_contour[min_x_idx], y_contour[min_x_idx])
    
    # Find minimum y point on the contour
    min_y_idx = np.argmin(y_contour)
    min_y_point = (x_contour[min_y_idx], y_contour[min_y_idx])
    
    # Add label for the Pareto-optimal contour
    # Find a good position along the contour (e.g., at about 30% along the curve)
    label_idx = int(len(x_contour) * 0.3)
    ax.annotate('Pareto-optimal contour\nof k-eff = 1.00 solutions', 
                xy=(x_contour[label_idx], y_contour[label_idx]),
                xytext=(x_contour[label_idx] + 150, y_contour[label_idx] + 300),
                fontsize=13, fontweight='bold', color='darkred',
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.3', 
                               color='darkred', lw=1.5),
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', 
                         edgecolor='darkred', alpha=0.8))
    
    # Add dot and label for minimum x point
    ax.plot(min_x_point[0], min_x_point[1], 'o', color='blue', markersize=10, zorder=5)
    ax.annotate(f'Minimum cubes\n({min_x_point[0]:.0f} cubes, {min_x_point[1]:.0f} L)', 
                xy=min_x_point,
                xytext=(min_x_point[0] - 200, min_x_point[1] - 400),
                fontsize=12, fontweight='bold', color='blue',
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.3', 
                               color='blue', lw=1.5),
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', 
                         edgecolor='blue', alpha=0.8))
    
    # Add dot and label for minimum y point
    ax.plot(min_y_point[0], min_y_point[1], 'o', color='green', markersize=10, zorder=5)
    ax.annotate(f'Minimum D₂O\n({min_y_point[0]:.0f} cubes, {min_y_point[1]:.0f} L)', 
                xy=min_y_point,
                xytext=(min_y_point[0] + 200, min_y_point[1] - 300),
                fontsize=12, fontweight='bold', color='green',
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.3', 
                               color='green', lw=1.5),
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', 
                         edgecolor='green', alpha=0.8))

    # Add fiducial B8 point at 664 cubes and 1400 liters
    fiducial_point = (664, 1400)
    ax.plot(fiducial_point[0], fiducial_point[1], 'o', color='purple', markersize=10, zorder=5)
    ax.annotate('Fiducial B8\n(664 cubes, 1400 L)', 
                xy=fiducial_point,
                xytext=(fiducial_point[0] - 250, fiducial_point[1] + 300),
                fontsize=12, fontweight='bold', color='purple',
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.3', 
                               color='purple', lw=1.5),
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', 
                         edgecolor='purple', alpha=0.8))

    fig.tight_layout()
    plt.show()


"""
Helper functions
"""
CUBE_VOL_CM3   = 125.0
CUBE_VOL_L     = CUBE_VOL_CM3 / 1000.0  # 0.125 L per cube
U_DENS_G_CM3   = 18.5349
CUBE_MASS_KG   = (CUBE_VOL_CM3 * U_DENS_G_CM3) / 1000.0  # ≈ 2.3168625 kg per cube

def liters_to_kg(L):
    """Convert liters of D2O (ρ = 1.1 g/cm^3) to kilograms."""
    return L * 1.106104

def kg_to_liters(kg):
    """Convert kilograms of D2O (ρ = 1.1 g/cm^3) to liters."""
    return kg / 1.106104 # Convert kg hwtr to liters (1.10)

def cubes_to_kg(nc):
    """."""
    return nc * CUBE_MASS_KG # Convert number of cubes to kg (each 125 cc, 18.5349 g/cc)

def kg_to_cubes(kg):
    return kg / CUBE_MASS_KG # Convert kg cubes to number of cubes.

def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    """Return a truncated copy of a matplotlib colormap."""
    new_cmap = mcolors.LinearSegmentedColormap.from_list(
        f'trunc({cmap.name},{minval:.2f},{maxval:.2f})',
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap

def gaussian_filter_nan(Z, sigma):
    """
    Apply a Gaussian filter to an array with NaNs by:
      1- filtering values with NaNs replaced by 0,
      2- filtering a weight mask,
      3- dividing filtered values by filtered weights.
    This prevents NaNs (from convex hull gaps) from bleeding into valid regions.
    """
    values = np.nan_to_num(Z, nan=0.0)
    weights = np.isfinite(Z).astype(float)

    values_f = gaussian_filter(values, sigma=sigma, mode="nearest")
    weights_f = gaussian_filter(weights, sigma=sigma, mode="nearest")

    with np.errstate(invalid='ignore', divide='ignore'):
        Z_smooth = values_f / weights_f
    Z_smooth[weights_f == 0] = np.nan
    return Z_smooth

if __name__ == '__main__':
    main()


