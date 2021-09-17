"""
VOID COEFFICIENT (MCNP)

Written by Patrick Park (RO, Physics '22)
ppark@reed.edu

Adapted from the Reed Automated Neutronics Engine for the Haigerloch project

Created Mar. 13, 2021

__________________
Default MCNP units

Length: cm
Mass: g
Energy & Temp.: MeV
Positive density (+x): atoms/barn-cm
Negative density (-x): g/cm3
Time: shakes
(1 barn = 10e-24 cm2, 1 sh = 10e-8 sec)

_______________
Technical Notes

"""

import os, sys, multiprocessing
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from scipy import stats
from scipy.optimize import curve_fit
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

from haigerloch_mcnp_funcs import *

FILEPATH = os.path.dirname(os.path.abspath(__file__))
HEAVY_WATER_MAT_CARD = '10201'
HEAVY_WATER_DENSITIES = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0] # np.arange(start=0.1,stop=1.0,step=0.1)
# Prefer hardcoded lists rather than np.arange, which produces imprecise floating points, e.g., 0.7000000...003
INPUTS_FOLDER_NAME = 'inputs'
OUTPUTS_FOLDER_NAME = 'outputs'
MODULE_NAME = 'void'


def main():
    initialize_rane()
    BASE_INPUT_NAME = find_base_file(FILEPATH)
    check_kcode(FILEPATH, BASE_INPUT_NAME)

    KEFF_CSV_NAME = f'{BASE_INPUT_NAME.split(".")[0]}_keff.csv'
    RHO_CSV_NAME = f'{BASE_INPUT_NAME.split(".")[0]}_rho.csv'
    PARAMS_CSV_NAME = f'{BASE_INPUT_NAME.split(".")[0]}_parameters.csv'
    FIGURE_NAME = f'{BASE_INPUT_NAME.split(".")[0]}_results.png'

    """
    print("The following lines will ask desired rod heights for this calculation.")
    
    rod_heights_dict = {}
    for rod in RODS:
        height = input(f"Input desired integer height for the {rod} rod: ")
        rod_heights_dict[rod] = height
    
    input_created = change_rod_height(FILEPATH, MODULE_NAME, rod_heights_dict, BASE_INPUT_NAME, INPUTS_FOLDER_NAME)
    if input_created: print(f"Created {num_inputs_created} new input deck.")
    if not input_created: print(f"\n--Skipped {num_inputs_skipped} input deck because it already exists.")
    """

    num_inputs_created = 0
    num_inputs_skipped = 0
    for i in range(0, len(HEAVY_WATER_DENSITIES)):
        cell_densities_dict = {HEAVY_WATER_MAT_CARD: HEAVY_WATER_DENSITIES[i]}
        input_created = change_cell_densities(FILEPATH, MODULE_NAME, cell_densities_dict, BASE_INPUT_NAME, INPUTS_FOLDER_NAME)
        if input_created: num_inputs_created += 1
        if not input_created: num_inputs_skipped += 1

    print(f"Created {num_inputs_created} new input decks.\n"
          f"--Skipped {num_inputs_skipped} input decks because they already exist.")

    if not check_run_mcnp(): sys.exit()

    # Run MCNP for all .i files in f".\{inputs_folder_name}".
    tasks = get_tasks()
    for file in os.listdir(f"{FILEPATH}/{INPUTS_FOLDER_NAME}"):
        run_mcnp(FILEPATH,f"{FILEPATH}/{INPUTS_FOLDER_NAME}/{file}",OUTPUTS_FOLDER_NAME,tasks)

    # Deletes MCNP runtape and source dist files.
    delete_files(f"{FILEPATH}/{OUTPUTS_FOLDER_NAME}",r=True,s=True)

    # Setup a dataframe to collect keff values
    keff_df = pd.DataFrame(columns=["density", "keff", "keff unc"]) # use lower cases to match 'rods' def above
    keff_df["density"] = HEAVY_WATER_DENSITIES
    keff_df.set_index("density",inplace=True)

    for water_density in HEAVY_WATER_DENSITIES:
        keff, keff_unc = extract_keff(f"{FILEPATH}/{OUTPUTS_FOLDER_NAME}/o_{BASE_INPUT_NAME.split('.')[0]}-{MODULE_NAME}-m{HEAVY_WATER_MAT_CARD}-{''.join(c for c in str(water_density) if c not in '.')}.o")
        keff_df.loc[water_density, 'keff'] = keff
        keff_df.loc[water_density, 'keff unc'] = keff_unc

    print(f"\nDataframe of keff values and their uncertainties:\n{keff_df}\n")
    keff_df.to_csv(KEFF_CSV_NAME)

    convert_keff_to_rho_coef(KEFF_CSV_NAME, RHO_CSV_NAME)
    calc_params_coef(RHO_CSV_NAME, PARAMS_CSV_NAME, MODULE_NAME)
    for rho_or_dollars in ['rho','dollars']: plot_data_void(KEFF_CSV_NAME, RHO_CSV_NAME, PARAMS_CSV_NAME, FIGURE_NAME, rho_or_dollars, for_fun=True)

    print(f"\n************************ PROGRAM COMPLETE ************************\n")




'''
Plots integral and differential worths given a CSV of rho and uncertainties.

rho_csv_name: str, name of CSV of rho and uncertainties, e.g. "rho.csv"
figure_name: str, desired name of resulting figure, e.g. "figure.png"

Does not return anything. Only produces a figure.

NB: Major plot settings have been organized into variables for your personal convenience.
'''
def plot_data_void(keff_csv_name, rho_csv_name, params_csv_name, figure_name, rho_or_dollars, for_fun=False):
    if rho_or_dollars.lower() in ['r','p','rho']: rho_or_dollars = 'rho'
    elif rho_or_dollars.lower() in ['d','dollar','dollars']: rho_or_dollars = 'dollars'

    keff_df = pd.read_csv(keff_csv_name, index_col=0)
    rho_df = pd.read_csv(rho_csv_name, index_col=0)
    params_df = pd.read_csv(params_csv_name, index_col=0)
    water_densities = rho_df.index.values.tolist()

    # Personal parameters, to be used in plot settings below.
    label_fontsize = 16
    legend_fontsize = "x-large"
    # fontsize: int or {'xx-small', 'x-small', 'small', 'medium', 'large', 'x-large', 'xx-large'}
    my_dpi = 320
    x_label = r"Heavy water density "# (g/cm$^3$)"
    y_label_keff, y_label_rho, y_label_void = r"Effective multiplication factor ($k_{eff}$)", \
                                              r"Reactivity ($\%\Delta k/k$)", \
                                              r"Void coefficient ((%$\Delta k/k$)/%)"
    if rho_or_dollars == 'dollars':
        y_label_rho, y_label_void= r"Reactivity ($\Delta$\$)", r"Void coefficient (\$/%)"

    plot_color = ["tab:red","tab:blue","tab:green"]

    ax_x_min, ax_x_max = 0.05, 1.05
    ax_x_major_ticks_interval, ax_x_minor_ticks_interval = 0.1, 0.025
    if for_fun:
        ax_x_min, ax_x_max = 0, 2
        ax_x_major_ticks_interval, ax_x_minor_ticks_interval = 0.1, 0.05

    ax_keff_y_min, ax_keff_y_max = 0.85, 1.10
    ax_keff_y_major_ticks_interval, ax_keff_y_minor_ticks_interval = 0.05, 0.01

    ax_rho_y_min, ax_rho_y_max = -16, 1
    ax_rho_y_major_ticks_interval, ax_rho_y_minor_ticks_interval = 2, 1
    if rho_or_dollars == 'dollars':
        ax_rho_y_min, ax_rho_y_max = -21, 1.0
        ax_rho_y_major_ticks_interval, ax_rho_y_minor_ticks_interval = 2, 1

    ax_void_y_min, ax_void_y_max = -0.4, 0.1
    ax_void_y_major_ticks_interval, ax_void_y_minor_ticks_interval = 0.1, 0.025
    if rho_or_dollars == 'dollars':
        ax_void_y_min, ax_void_y_max = -0.5, 0.1
        ax_void_y_major_ticks_interval, ax_void_y_minor_ticks_interval = 0.1, 0.025

    fig, axs = plt.subplots(3, 1, figsize=(1636 / 96, 3 * 673 / 96), dpi=my_dpi, facecolor='w', edgecolor='k')
    ax_keff, ax_rho, ax_void = axs[0], axs[1], axs[2]  # integral, differential worth on top, bottom, resp.

    # Plot data for keff.
    x = [water_density for water_density in water_densities if water_density <= 1]
    if for_fun: x = water_densities
    x_fit = np.linspace(min(x), max(x), len(water_densities))
    y_keff, y_keff_unc = [], []
    for water_density in x:
        y_keff.append(keff_df.loc[water_density,'keff']), y_keff_unc.append(keff_df.loc[water_density,'keff unc'])

    ax_keff.errorbar(x, y_keff, yerr=y_keff_unc,
                     marker="o", ls="none",
                     color=plot_color[0], elinewidth=2, capsize=3, capthick=2)

    eq_keff = find_poly_reg(x, y_keff, 2)['polynomial']  # n=2 order fit
    r2_keff = find_poly_reg(x, y_keff, 2)['r-squared']
    sd_keff = np.average(np.abs(np.polyval(np.polyfit(x, y_keff, 2), x) - y_keff))
    y_fit_keff = np.polyval(eq_keff, x)

    ax_keff.plot(x, y_fit_keff, color=plot_color[0],
                 label=r'y=-{:.3f}$x^2$+{:.2f}$x$+{:.2f},  $R^2$={:.2f},  $\sigma$={:.4f}'.format(
                     np.abs(eq_keff[0]),eq_keff[1], eq_keff[2], r2_keff, sd_keff))

    # Plot data for reactivity
    y_rho, y_rho_unc = [], []
    for water_density in x:
        if rho_or_dollars == 'rho': y_rho.append(rho_df.loc[water_density,'rho']), y_rho_unc.append(rho_df.loc[water_density,'rho unc'])
        if rho_or_dollars == 'dollars': y_rho.append(rho_df.loc[water_density, 'dollars']), y_rho_unc.append(rho_df.loc[water_density, 'dollars unc'])

    ax_rho.errorbar(x, y_rho, yerr=y_rho_unc,
                     marker="o", ls="none",
                     color=plot_color[1], elinewidth=2, capsize=3, capthick=2)

    eq_rho = find_poly_reg(x, y_rho, 2)['polynomial']  # n=2 order fit
    r2_rho = find_poly_reg(x, y_rho, 2)['r-squared']
    sd_rho = np.average(np.abs(np.polyval(np.polyfit(x, y_rho, 2), x) - y_rho))
    y_fit_rho = np.polyval(eq_rho, x_fit)

    ax_rho.plot(x_fit, y_fit_rho, color=plot_color[1],
                label=r'y=-{:.1f}$x^2$+{:.0f}$x${:.0f},  $R^2$={:.2f},  $\sigma$={:.2f}'.format(
                    np.abs(eq_rho[0]), eq_rho[1], eq_rho[2], r2_rho, sd_rho))

    # Plot data for coef_void
    y_void, y_void_unc = [], []
    for water_density in x:
        if rho_or_dollars == 'rho': y_void.append(params_df.loc[water_density,'coef rho']), y_void_unc.append(params_df.loc[water_density, 'coef rho unc'])
        else: y_void.append(params_df.loc[water_density, 'coef dollars']), y_void_unc.append(params_df.loc[water_density, 'coef dollars unc'])

    ax_void.errorbar(x, y_void, yerr=y_void_unc,
                     marker="o", ls="none",
                     color=plot_color[2], elinewidth=2, capsize=3, capthick=2)

    eq_void = find_poly_reg(x, y_void, 1)['polynomial']
    r2_void = find_poly_reg(x, y_void, 1)['r-squared']
    sd_void = np.average(np.abs(np.polyval(np.polyfit(x, y_void, 1), x) - y_void))
    y_fit_void = np.polyval(eq_void, x_fit)

    ax_void.plot(x_fit, y_fit_void, color=plot_color[2],
                label=r'y={:.2f}$x${:.2f},  $R^2$={:.2f},  $\bar x$$\pm\sigma$={:.3f}$\pm${:.3f}'.format(
                    np.abs(eq_void[0]), eq_void[1], r2_void, np.mean(y_fit_void), sd_void))

    eq_void_der = -1*np.polyder(eq_rho)/100  # n=2 order fit
    y_fit_void_der = np.polyval(eq_void_der, x_fit)

    ax_void.plot(x_fit, y_fit_void_der, color=plot_color[2], linestyle='dashed',
                label=r'y={:.2f}$x${:.2f},  $\bar x$={:.3f}'.format(
                    np.abs(eq_void_der[0]), eq_void_der[1], np.mean(y_fit_void_der)))




    # Keff plot settings
    # ax_keff.set_xlim([ax_x_min, ax_x_max])
    # ax_keff.set_ylim([ax_keff_y_min, ax_keff_y_max])
     #ax_keff.xaxis.set_major_locator(MultipleLocator(ax_x_major_ticks_interval))
    # ax_keff.yaxis.set_major_locator(MultipleLocator(ax_keff_y_major_ticks_interval))
    ax_keff.minorticks_on()
    # ax_keff.xaxis.set_minor_locator(MultipleLocator(ax_x_minor_ticks_interval))
    # ax_keff.yaxis.set_minor_locator(MultipleLocator(ax_keff_y_minor_ticks_interval))
    ax_keff.autoscale(enable=True, axis='both')

    ax_keff.tick_params(axis='both', which='major', labelsize=label_fontsize)
    ax_keff.grid(b=True, which='major', color='#999999', linestyle='-', linewidth='1')
    ax_keff.grid(which='minor', linestyle=':', linewidth='1', color='gray')

    ax_keff.set_xlabel(x_label, fontsize=label_fontsize)
    ax_keff.set_ylabel(y_label_keff, fontsize=label_fontsize)
    ax_keff.legend(title=f'Key', title_fontsize=legend_fontsize, ncol=1, fontsize=legend_fontsize, loc='lower right')


    # Reactivity worth plot settings
    ax_rho.set_xlim([ax_x_min, ax_x_max])
    ax_rho.set_ylim([ax_rho_y_min, ax_rho_y_max])
    ax_rho.xaxis.set_major_locator(MultipleLocator(ax_x_major_ticks_interval))
    ax_rho.yaxis.set_major_locator(MultipleLocator(ax_rho_y_major_ticks_interval))
    ax_rho.minorticks_on()
    ax_rho.xaxis.set_minor_locator(MultipleLocator(ax_x_minor_ticks_interval))
    ax_rho.yaxis.set_minor_locator(MultipleLocator(ax_rho_y_minor_ticks_interval))

    # Use for 2 decimal places after 0. for dollars units
    if rho_or_dollars == "dollars": ax_rho.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

    ax_rho.tick_params(axis='both', which='major', labelsize=label_fontsize)
    ax_rho.grid(b=True, which='major', color='#999999', linestyle='-', linewidth='1')
    ax_rho.grid(which='minor', linestyle=':', linewidth='1', color='gray')

    ax_rho.set_xlabel(x_label, fontsize=label_fontsize)
    ax_rho.set_ylabel(y_label_rho, fontsize=label_fontsize)
    ax_rho.legend(title=f'Key', title_fontsize=legend_fontsize, ncol=1, fontsize=legend_fontsize, loc='lower right')


    # Void worth plot settings
    ax_void.set_xlim([ax_x_min, ax_x_max])
    ax_void.set_ylim([ax_void_y_min, ax_void_y_max])
    ax_void.xaxis.set_major_locator(MultipleLocator(ax_x_major_ticks_interval))
    ax_void.yaxis.set_major_locator(MultipleLocator(ax_void_y_major_ticks_interval))
    ax_void.minorticks_on()
    ax_void.xaxis.set_minor_locator(MultipleLocator(ax_x_minor_ticks_interval))
    ax_void.yaxis.set_minor_locator(MultipleLocator(ax_void_y_minor_ticks_interval))


    # Use for 2 decimal places after 0. for dollars units
    if rho_or_dollars == "dollars": ax_void.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

    ax_void.tick_params(axis='both', which='major', labelsize=label_fontsize)
    ax_void.grid(b=True, which='major', color='#999999', linestyle='-', linewidth='1')
    ax_void.grid(which='minor', linestyle=':', linewidth='1', color='gray')

    ax_void.set_xlabel(x_label, fontsize=label_fontsize)
    ax_void.set_ylabel(y_label_void, fontsize=label_fontsize)
    ax_void.legend(title=f'Key', title_fontsize=legend_fontsize, ncol=1, fontsize=legend_fontsize, loc='lower right')


    plt.savefig(f"{figure_name.split('.')[0]}_{rho_or_dollars}.{figure_name.split('.')[-1]}", bbox_inches='tight',
                pad_inches=0.1, dpi=my_dpi)
    print(
        f"\nFigure '{figure_name.split('.')[0]}_{rho_or_dollars}.{figure_name.split('.')[-1]}' saved!\n")  # no space near \


if __name__ == '__main__':
    main()