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

    data = data[ (data["cubes"] >= 500) & (data["cubes"] <= 2100) \
               & (data["modr v L"] >= 1200) & (data["modr v L"] <= 4000) ]

    # data["keff"] = data["keff"].round(3)

    c = data['cubes'].to_numpy()
    m = data['modr v L'].to_numpy()
    k = data['keff'].to_numpy()

    # Build interpolation grid
    xi = np.linspace(c.min(), c.max(), 400) # GRID_N = 500 : grid resolution per axis (< 1000 for speed; increase if needed)
    yi = np.linspace(m.min(), m.max(), 400)
    X, Y = np.meshgrid(xi, yi)

    # Interpolant. Use linear to avoid ringing (which you can get in cubic)
    Z_lin = griddata((c, m), k, (X, Y), method='linear') # linear, cubic

    # Smooth with Gaussian filter   
    Z = gaussian_filter_nan(Z_lin, sigma=6) # sigma: Gaussian blur strength in grid cells



    """
    PLOTTING
    """
    
    LEVELS = np.linspace(0.90, 1.02, num=13)
    FONTSIZE = 15

    """ Plot settings """
    plt.rc('font', family='Arial', size=FONTSIZE)
    fig, ax = plt.subplots(figsize=(16, 9))


    """ Contour lines """
    original_cmap = plt.get_cmap('coolwarm')
    truncated_cmap = truncate_colormap(original_cmap, minval=0.275, maxval=1.0)
    truncated_cmap.set_under("#8db0fe")

    k_1_contour    = ax.contour( X, Y, Z, levels=[1.00], colors='black', linewidths=0,)
    contour_filled = ax.contourf(X, Y, Z, levels=LEVELS, cmap=truncated_cmap, extend="min")
    contour_lines  = ax.contour( X, Y, Z, levels=LEVELS, colors='black', linewidths=0.5)

    # Extract the path vertices of the k-eff = 1.00 contour line
    path = k_1_contour.get_paths()[0]
    vertices = path.vertices
    x_contour = vertices[:, 0]
    y_contour = vertices[:, 1]

    # Increase space between right y-axis and colorbar
    cbar = fig.colorbar(contour_filled, ax=ax, pad=0.08, fraction=0.035) 
    ax.clabel(contour_lines, inline=True, fontsize=FONTSIZE, fmt='%1.2f')
    ax.grid(which='major', linestyle='-', linewidth=0.5, color='black', alpha=0.5)
    
    """ Show individual data points from each MCNP run """
    # ax.scatter(c, m, s=12, color='k', alpha=0.15, zorder=3)  # keep points, but deemphasize

    """ Optimal V_M / V_F line """
    # Dotted line for optimal V_M/V_F ratio = V_D2O / V_U = 18.6
    x_line = np.linspace(c.min(), c.max(), 500)
    y_line = 18.6 * CUBE_VOL_L * x_line
    ax.plot(x_line, y_line, linestyle=':', linewidth=2, color='k')

    # Compute slope and rotation angle
    slope = (y_line[-1] - y_line[0]) / (x_line[-1] - x_line[0]) 
    angle = np.degrees(np.arctan(slope)) - 28.25

    # Place label lower on the line (x*100% up from start)
    pos_idx = int(len(x_line) * 0.3)

    ax.text(
        x_line[pos_idx]-30, y_line[pos_idx]+30,
        r"Optimal V$_M$ $/$ V$_F$ = 18.6",
        rotation=angle,
        ha='center', va='center',
        fontsize=FONTSIZE, color='black',
        bbox=dict(boxstyle="square,pad=0.2", facecolor='white', edgecolor='black', alpha=0.8) )
    


    
    # Find minimum x point on the contour
    min_x_idx = np.argmin(x_contour)
    min_x_point = (x_contour[min_x_idx], y_contour[min_x_idx])
    
    # Find minimum y point on the contour
    min_y_idx = np.argmin(y_contour)
    min_y_point = (x_contour[min_y_idx], y_contour[min_y_idx])
    
    # Add label for the Pareto-optimal contour
    # Find a good position along the contour (at x*100% along the curve)
    label_idx = int(len(x_contour) * 0.15)
    ax.annotate(r'Pareto-optimal contour\nof k$_eff$ = 1.00 solutions', 
                xy=(x_contour[label_idx], y_contour[label_idx]),
                xytext=(x_contour[label_idx] - 300, y_contour[label_idx] + 200),
                fontsize=FONTSIZE, color='black',
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.3', 
                               color='black', lw=1),
                bbox=dict(boxstyle="square,pad=0.3", facecolor='white', 
                         edgecolor='black', alpha=0.8))
    
    # Add dot and label for minimum x point
    ax.plot(min_x_point[0], min_x_point[1], 'o', color='black', markersize=6, zorder=5)
    ax.annotate(f'Minimum cubes\n({min_x_point[0]:.0f} cubes, {min_x_point[1]:.0f} L)\n({cubes_to_kg(min_x_point[0]):.0f} kg, {liters_to_kg(min_x_point[1]):.0f} kg)', 
                xy=min_x_point,
                xytext=(min_x_point[0] - 275, min_x_point[1] - 300),
                fontsize=FONTSIZE, color='black',
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.3', 
                               color='black', lw=1),
                bbox=dict(boxstyle="square,pad=0.3", facecolor='white', 
                         edgecolor='black', alpha=0.8))
    
    # Add dot and label for minimum y point
    ax.plot(min_y_point[0], min_y_point[1], 'o', color='black', markersize=6, zorder=5)
    ax.annotate(f'Minimum D$_2$O\n({min_y_point[0]:.0f} cubes, {min_y_point[1]:.0f} L)\n({cubes_to_kg(min_y_point[0]):.0f} kg, {liters_to_kg(min_y_point[1]):.0f} kg)', 
                xy=min_y_point,
                xytext=(min_y_point[0] + 25, min_y_point[1] - 250),
                fontsize=FONTSIZE, color='black',
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.3', 
                               color='black', lw=1),
                bbox=dict(boxstyle="square,pad=0.3", facecolor='white', 
                         edgecolor='black', alpha=0.8))

    # Add fiducial B8 point at 664 cubes and 1400 liters
    fiducial_point = (664, 1400)
    ax.plot(fiducial_point[0], fiducial_point[1], 'o', color='black', markersize=6, zorder=5)
    ax.annotate(f'Fiducial B8\n(664 cubes, 1400 L)\n({cubes_to_kg(664):.0f} kg, {liters_to_kg(1400):.0f} kgL)', 
                xy=fiducial_point,
                xytext=(fiducial_point[0] + 225, fiducial_point[1] + 225),
                fontsize=FONTSIZE, color='black',
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.3', 
                               color='black', lw=1),
                bbox=dict(boxstyle="square,pad=0.3", facecolor='white', 
                         edgecolor='black', alpha=0.5))

    # Slope/intercept of the optimal line: y = a*x + b
    a = 18.6 * CUBE_VOL_L
    b = 0.0

    # Find intersection between the polyline (k=1 contour) and the straight line
    xi = yi = None
    for i in range(len(x_contour) - 1):
        x1, y1 = x_contour[i],     y_contour[i]
        x2, y2 = x_contour[i + 1], y_contour[i + 1]

        f1 = y1 - (a * x1 + b)
        f2 = y2 - (a * x2 + b)

        # Check if the segment straddles the line 
        if f1 == 0:
            xi, yi = x1, y1
            break
        if f1 * f2 <= 0:
            dx, dy = x2 - x1, y2 - y1
            denom = dy - a * dx
            if abs(denom) < 1e-12:
                continue  # segment nearly parallel to the line; skip
            t = (a * x1 + b - y1) / denom  # param along the segment
            if 0.0 <= t <= 1.0:
                xi = x1 + t * dx
                yi = y1 + t * dy
                break

    # If an intersection was found, plot a dot and label
    if xi is not None and yi is not None:
        ax.plot(xi, yi, 'o', color='black', markersize=6, zorder=6)
        ax.annotate(
            f'Intersection (k-eff=1)\n({xi:.0f} cubes, {yi:.0f} L)\n'
            f'({cubes_to_kg(xi):.0f} kg, {liters_to_kg(yi):.0f} kg)',
            xy=(xi, yi),
            xytext=(xi + 200, yi + 150),  # tweak 
            fontsize=FONTSIZE, color='black',
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.2',
                            color='black', lw=1),
            bbox=dict(boxstyle="square,pad=0.3", facecolor='white',
                      edgecolor='black', alpha=0.8)
        )
    else:
        print("Warning: no intersection found between k=1 contour and the 18.6 line.")

    # Primary axes
    ax.set_xlabel(r'Number of uranium cubes', fontsize=FONTSIZE)
    ax.set_ylabel('96.8%-pure heavy water volume [L]', fontsize=FONTSIZE)
    cbar.set_label('Effective multiplication [k-eff]', fontsize=FONTSIZE)

    ax.minorticks_on()
    ax.set_xticks(np.arange(500, 2101, step=200))
    ax.set_yticks(np.arange(1200, 4001, step=400))

    # Change tick lengths for y-axis
    ax.tick_params(axis="x", which="major", length=6)  # major ticks
    ax.tick_params(axis="x", which="minor", length=3)  # minor ticks
    ax.tick_params(axis="y", which="major", length=6)  # major ticks
    ax.tick_params(axis="y", which="minor", length=3)  # minor ticks

    ax.set_xlim(500, 2100)
    ax.set_ylim(1200, 4000)

    # Secondary axes
    # Right y: liters -> kg 
    secax_y = ax.secondary_yaxis('right', functions=(liters_to_kg, kg_to_liters))
    secax_y.set_ylabel(r'96.8%-pure heavy water mass [kg]', fontsize=FONTSIZE) # (1.11 g/cm$^3$)
    secax_y.tick_params(axis='y', pad=2)  # pad: space between ticks and label

    # Top x: number of cubes -> kg 
    secax_x = ax.secondary_xaxis('top', functions=(cubes_to_kg, kg_to_cubes))
    secax_x.tick_params(axis='x', pad=0)  # pad: space between ticks and label
    secax_x.set_xlabel(r'Uranium mass [kg]', fontsize=FONTSIZE) # (18.53 g/cm$^3$)

    # Change tick lengths for y-axis
    secax_x.tick_params(axis="x", which="major", length=6)  # major ticks
    secax_x.tick_params(axis="x", which="minor", length=3)  # minor ticks
    secax_y.tick_params(axis="y", which="major", length=6)  # major ticks
    secax_y.tick_params(axis="y", which="minor", length=3)  # minor ticks

    fig.tight_layout()
    # plt.savefig("./Figure/contour_extra_labels.png", dpi=600, bbox_inches="tight", pad_inches=0.01)
    # plt.savefig("./Figure/contour_extra_labels.pdf", bbox_inches="tight", pad_inches=0.01)
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


