import os
import sys
import fnmatch
import traceback, sys
import fileinput
import numpy as np
import shutil
import platform
import json
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.axes3d import Axes3D, get_test_data
from matplotlib import cm as cmx  
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import matplotlib.colors as colors
from scipy.interpolate import UnivariateSpline

from MCNP_File import *
from Utilities import *
from Parameters import *
from plotStyles import *


class Reactivity(MCNP_File):

    def process_rcty_keff(self):

        """
        Output results filepaths
        """
        self.keff_filename = f"{self.base_filename}_{self.run_type}_keff.csv"
        self.keff_filepath = f"{self.results_folder}/{self.keff_filename}"

        print(f'\n processing: {self.output_filename}')

        self.extract_keff()

        """
        Define the index column and data to be used in dataframe
        """
        self.d2o_temp_C  = float('{:.2f}'.format(self.d2o_temp_K - 273))
        self.fuel_temp_C = float('{:.2f}'.format(self.fuel_temp_K - 273)) # use 273 not 273
        if self.run_type == 'rcty_fuel':
            self.index_header, self.index_data = 'temp (C)', UZRH_FUEL_TEMPS_C
            self.row_val = self.fuel_temp_C # make sure index_data and row_val use same units!
        elif self.run_type == 'rcty_modr':
            self.index_header, self.index_data = 'temp (C)', D2O_MOD_TEMPS_C
            self.row_val = self.d2o_temp_C
        elif self.run_type == 'rcty_pure':
            self.index_header, self.index_data = 'd2o purity (at%)', D2O_MOD_PURITIES
            self.row_val = self.d2o_purity

        """
        Setup or read keff dataframe
        """
        if self.keff_filename in os.listdir(self.results_folder):
            try:
                df_keff = pd.read_csv(self.keff_filepath, encoding='utf8')
                df_keff.set_index(self.index_header, inplace=True)
            except:
                print(f"\n   fatal. Cannot read {self.keff_filename}")
                print(f"   fatal.   Ensure that:")
                print(f"   fatal.     - the file is a .csv")
                print(f"   fatal.     - the index (first column) header is '{self.index_header}'")
                sys.exit(2)
        else:
            print(f'\n   comment. creating new results file {self.keff_filepath}')
            df_keff = pd.DataFrame(self.index_data, columns=[self.index_header])
            df_keff.set_index(self.index_header, inplace=True)
            df_keff["SaB lib"] = 0.0
            df_keff["keff"] = 0.0 
            df_keff["keff unc"] = 0.0 

        """
        Populate the dataframe with keff and unc values
        """
        if self.run_type == 'rcty_modr':
            df_keff.loc[self.row_val, "density"] = self.d2o_density
            df_keff.loc[self.row_val, "SaB lib"] = self.d_d2o_sab_lib
        elif self.run_type == 'rcty_fuel':
            df_keff.loc[self.row_val, "SaB lib"] = self.h_zr_mt_lib
        df_keff.loc[self.row_val, "keff"] = self.keff
        df_keff.loc[self.row_val, "keff unc"] = self.keff_unc
        df_keff.loc[self.row_val, "therm n %"] = self.therm_n_frac

        # put df in increasing order based on the index column, USE inplace=False
        df_keff = df_keff.sort_values(by=self.index_header, ascending=True,inplace=False) 
        
        df_keff.to_csv(self.keff_filepath, encoding='utf8')


    def process_rcty_rho(self):

        self.rho_filename = f"{self.base_filename}_{self.run_type}_rho.csv"
        self.rho_filepath = f"{self.results_folder}/{self.rho_filename}"

        df_keff = pd.read_csv(self.keff_filepath, index_col=0)

        """
        Setup or read rho dataframe
        """
        if self.rho_filename in os.listdir(self.results_folder):
            try:
                df_rho = pd.read_csv(self.rho_filepath, encoding='utf8')
                df_rho.set_index(self.index_header, inplace=True)
            except:
                print(f"\n   fatal. Cannot read {self.rho_filename}")
                print(f"   fatal.   Ensure that:")
                print(f"   fatal.     - the file is a .csv")
                print(f"   fatal.     - the index (first column) header is '{self.index_header}'")
                sys.exit(2)
        else:
            print(f'\n   comment. creating new results file {self.rho_filepath}')
            df_rho = pd.DataFrame(self.index_data, columns=[self.index_header])
            df_rho.set_index(self.index_header, inplace=True)
            df_rho["rho"], df_rho["rho unc"] = 0.0, 0.0 

        '''
        ERROR PROPAGATION FORMULAE
        % Delta rho = 100* frac{k2-k1}{k2*k1}
        numerator = k2-k1
        delta num = sqrt{(delta k2)^2 + (delta k1)^2}
        denominator = k2*k1
        delta denom = k2*k1*sqrt{(frac{delta k2}{k2})^2 + (frac{delta k1}{k1})^2}
        delta % Delta rho = 100*sqrt{(frac{delta num}{num})^2 + (frac{delta denom}{denom})^2}
        '''
        for x_value in self.index_data:
            k1 = df_keff.loc[x_value, 'keff']
            k2 = df_keff.loc[min(self.index_data), 'keff']
            dk1 = df_keff.loc[x_value, 'keff unc']
            dk2 = df_keff.loc[min(self.index_data), 'keff unc']
            k2_minus_k1 = k2 - k1
            k2_times_k1 = k2 * k1
            d_k2_minus_k1 = np.sqrt(dk2 ** 2 + dk1 ** 2)
            d_k2_times_k1 = k2 * k1 * np.sqrt((dk2 / k2) ** 2 + (dk1 / k1) ** 2)
            rho = (k1 - k2) / (k2 * k1) * 100
            dollars = 0.01 * rho / BETA_EFF

            df_rho.loc[x_value, 'rho'] = rho
            df_rho.loc[x_value, 'dollars'] = dollars
            # while the 'dollars' (and 'dollars unc') columns are not in the original df_rho definition,
            # simply defining a value inside it automatically adds the column
            if k2_minus_k1 != 0:
                rho_unc = rho * np.sqrt((d_k2_minus_k1 / k2_minus_k1) ** 2 + (d_k2_times_k1 / k2_times_k1) ** 2)
                dollars_unc = rho_unc / 100 / BETA_EFF
                df_rho.loc[x_value, 'rho unc'], df_rho.loc[x_value, 'dollars unc'] = rho_unc, dollars_unc
            else:
                df_rho.loc[x_value, 'rho unc'], df_rho.loc[x_value, 'dollars unc'] = 0, 0

        print(f"\nDataframe of rho values and their uncertainties:\n{df_rho}\n")
        df_rho.to_csv(self.rho_filepath, encoding='utf8')


    def process_rcty_coef(self):
        ''' Translate df_rho to df_coef 
        '''
        self.coef_filename = f"{self.base_filename}_{self.run_type}_coef.csv"
        self.coef_filepath = f"{self.results_folder}/{self.coef_filename}"

        print(f'\n Calculating coef from: {self.rho_filepath} \n')
        try:
            df_rho = pd.read_csv(self.rho_filepath)
            df_rho.set_index(self.index_header, inplace=True)
            df_coef = df_rho.copy()
        except:
            print(f'\n   fatal. (ReactivityOutputFile.py) error converting rho csv to coef csv \n')
            sys.exit()

        for col in [c for c in df_rho if 'unc' not in c]:
            for x in list(df_rho.index.values):
                try: 
                    if x == min(self.index_data):
                        df_coef.loc[x, col] = 0.0
                        df_coef.loc[x, col+' unc'] = 0.0
                    else:
                        dx = x - min(list(df_rho.index.values))
                        coef, coef_unc = df_rho.loc[x, col]/dx, df_rho.loc[x, col+' unc']/dx # don't divide unc by dx
                        df_coef.loc[x, col] = coef
                        df_coef.loc[x, col+' unc'] = coef_unc
                except:
                    print(f"\n   warning. (ReactivityOutputFile.py) error calculating coef for value {x} in cycle state {col}.")
                    print(f"   warning. It is possible you did not specify calculations to be run for cycle state {col}.") 
                    print(f"   warning. Skipping... \n")

        df_coef.to_csv(self.coef_filepath, encoding='utf8')


    def plot_rcty_coef(self):

        df_keff = pd.read_csv(self.keff_filepath)
        df_rho  = pd.read_csv(self.rho_filepath)
        df_coef = pd.read_csv(self.coef_filepath)

        df_keff['keff unc'] = 3 * df_keff['keff unc'] # get 3-sigma errors bc 1-sigma (default) is too small
        df_rho['rho unc'] = 3 * df_rho['rho unc'] # get 3-sigma errors bc 1-sigma (default) is too small
        # df_coef['coef unc'] = 3 * df_coef['dollars unc'] # get 3-sigma errors bc 1-sigma (default) is too small

        df_keff.set_index(self.index_header, inplace=True)
        df_rho.set_index(self.index_header, inplace=True)
    
        # bank = self.rod_heights_dict['bank']
        if self.run_type == 'rcty_modr':
            self.rcty_label   = 'moderator' # line label
            self.x_axis_label = f'Water temperature [°C]' # ({bank}% bank)' # x axis label
            self.y_axis_label = 'Moderator temp. coef.' # y axis label of 3rd plot (axs[2])
            self.y_axis_label_unit = '°C' # unit to use on y axis label of 2nd & 3rd plots (axs[1], axs[2])
        elif self.run_type == 'rcty_fuel':
            self.rcty_label   = 'fuel' 
            self.x_axis_label = f'Fuel temperature [°C]' # ({bank}% bank)'
            self.y_axis_label = 'Fuel temp. coef.'
            self.y_axis_label_unit = '°C'
        elif self.run_type == 'rcty_void':
            self.rcty_label   = 'void' 
            self.x_axis_label = f'Water void [at%]' # ({bank}% bank)'
            self.y_axis_label = 'Void coefficient'
            self.y_axis_label_unit = 'g/cc'
        else:
            print("\n   fatal. reactivity coefficent plot labels not defined")
            sys.exit()


        for rho_or_dollars in ['rho', 'dollars']:
            fig, axs = plt.subplots(3,1, figsize=FIGSIZE,facecolor='w',edgecolor='k')
            axs = axs.ravel()

            rods = [c for c in df_rho.columns.values.tolist() if "unc" not in c]
            heights = list(df_keff.index.values)

            # linestyle = ['-': solid, '--': dashed, '-.' dashdot, ':': dot]

            for i in [0,1,2]:
                if self.run_type in ['rcty_void']:
                    axs[i].set_xlim([0,20])
                    axs[i].xaxis.set_major_locator(MultipleLocator(1))
                elif self.run_type in ['rcty_modr']:
                    axs[i].set_xlim([15,100])
                    axs[i].xaxis.set_major_locator(MultipleLocator(10))
                elif self.run_type in ['rcty_fuel']:
                    axs[i].set_xlim([0,1000])
                    axs[i].xaxis.set_major_locator(MultipleLocator(100))
                axs[i].set_xlabel(self.x_axis_label)
                axs[i].autoscale(axis='y')
                axs[i].tick_params(axis='both', which='major', length=10, direction='in', bottom=True, top=True, left=True, right=True)
                # axs[i].grid(b=True, which='major', color='#999999', linestyle='-', linewidth='1')
            
            axs[0].set_ylabel(r'Eff. multiplication factor [$k_{eff}\pm 3\sigma$]')
            axs[1].set_ylabel('Reactivity [%Δρ±3σ]')
            if rho_or_dollars == 'dollars':
                axs[1].set_ylabel('Reactivity [Δ$±3σ]')
                axs[1].yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
            axs[2].set_ylabel(f'{self.y_axis_label} [%Δρ/{self.y_axis_label_unit}±3σ]')
            if rho_or_dollars == 'dollars':
                axs[2].set_ylabel(f'{self.y_axis_label} [Δ$/{self.y_axis_label_unit}±3σ]')
                axs[2].yaxis.set_major_formatter(FormatStrFormatter('%.4f'))


            """
            Keff plot
            """
            ax = axs[0]

            y     = df_keff[f"keff"].tolist()
            y_unc = df_keff[f"keff unc"].tolist()
            
            ax.errorbar(heights, y, yerr=y_unc,
                        marker=MARKER_STYLES[self.run_type], markersize=MARKER_SIZE,
                        color=LINE_COLORS[self.run_type],
                        ls="none", elinewidth=2, capsize=3, capthick=2)
                        
            if self.run_type in ['rcty_void']:
                eq_fit = find_poly_reg(heights,y,2)['polynomial'] # Utilities.py
                r2 = find_poly_reg(heights,y,2)['r-squared'] # Utilities.py
                eq_fit_str = 'y= -{:.3f}$x^2$ +{:.3f}$x$ +{:.3f}'.format(np.abs(eq_fit[0]), eq_fit[1], eq_fit[2])
            else:
                eq_fit = find_poly_reg(heights,y,1)['polynomial'] # Utilities.py
                r2 = find_poly_reg(heights,y,1)['r-squared'] # Utilities.py
                eq_fit_str = 'y= {:.2e}$x$ +{:.2e}'.format(np.abs(eq_fit[0]), eq_fit[1])

            sd = np.average(np.abs(np.polyval(eq_fit, heights) - y))
            r2_str = '{:.2f}'.format(r2)
            sd_str = '{:.2e}'.format(sd)

            y_fit  = np.polyval(eq_fit,heights)
            # spl = UnivariateSpline(heights, y) # use scipy spline to auto-fit smooth curve instead of guess-checking polyfit order
            
            # plot fit curve - replace 'y_fit' with 'spl(heights)' to plot smooth curve that connects-the-dots
            ax.plot(heights, y_fit, 
                    #label=r'{}, {}, $R^2$={}, $\Sigma$={}'.format(
                    #    self.rcty_label.capitalize(), eq_fit_str, r2_str, sd_str),
                    color=LINE_COLORS[self.run_type], linestyle=LINE_STYLES[self.run_type], linewidth=LINEWIDTH)
            # ax.legend(ncol=3, loc='lower right')
            # if self.run_type == 'rcty_fuel':
            #     ax.legend(ncol=3, loc='upper right')

            """
            reactivity plot
            """
            ax = axs[1]            

            y     = df_rho[f"rho"].tolist()
            y_unc = df_rho[f"rho unc"].tolist()
            if rho_or_dollars == 'dollars':
                y     = df_rho[f"dollars"].tolist()
                y_unc = df_rho[f"dollars unc"].tolist()

            # Data points with error bars
            ax.errorbar(heights, y, yerr=y_unc,
                        marker=MARKER_STYLES[self.run_type], markersize=MARKER_SIZE,
                        color=LINE_COLORS[self.run_type],
                        ls="none", elinewidth=2, capsize=3, capthick=2)

            # fit data to polynomial
            eq_fit = find_poly_reg(heights,y,1)['polynomial'] # Utilities.py
            r2 = find_poly_reg(heights,y,1)['r-squared'] # Utilities.py
            eq_fit_str = poly_to_latex(eq_fit) # Utilities.py

            sd = np.average(np.abs(np.polyval(eq_fit, heights) - y))
            r2_str = '{:.2f}'.format(r2)
            sd_str = '{:.2e}'.format(sd)

            y_fit  = np.polyval(eq_fit,heights)
            # spl = UnivariateSpline(heights, y) # use scipy spline to auto-fit smooth curve instead of guess-checking polyfit order
            
            # plot fit curve - replace 'y_fit' with 'spl(heights)' to plot smooth curve that connects-the-dots
            if self.run_type in ['rcty_fuel']:
                ax.plot(heights, y_fit, 
                        label=r'{}, $R^2$={}, $\Sigma$={}'.format(
                            eq_fit_str, r2_str, sd_str),
                        color=LINE_COLORS[self.run_type], linestyle=LINE_STYLES[self.run_type], linewidth=LINEWIDTH)
            else:
                ax.plot(heights, y_fit, 
                        color=LINE_COLORS[self.run_type], linestyle=LINE_STYLES[self.run_type], linewidth=LINEWIDTH)
            # ax.legend(ncol=3, loc='lower right')
            # if self.run_type == 'rcty_fuel':
            #     ax.legend(ncol=3, loc='upper right')

            """
            reactivity coefficient plot
            """
            ax = axs[2]
            x_min, x_idx = min(heights), heights.index(min(heights))
            heights = [h for h in heights if h != x_min]
            y     = [j for j in df_coef[f"rho"].tolist() if j != df_coef[f"rho"].tolist()[x_idx]]
            y_unc = [j for j in df_coef[f"rho unc"].tolist() if j != df_coef[f"rho unc"].tolist()[x_idx]]

            if rho_or_dollars == 'dollars':
                y     = [j for j in df_coef[f"dollars"].tolist() if j != df_coef[f"dollars"].tolist()[x_idx]]
                y_unc = [j for j in df_coef[f"dollars unc"].tolist() if j != df_coef[f"dollars unc"].tolist()[x_idx]]

            # Data points with error bars
            ax.errorbar(heights, y, yerr=y_unc,
                        marker=MARKER_STYLES[self.run_type], markersize=MARKER_SIZE,
                        color=LINE_COLORS[self.run_type],
                        ls="none", elinewidth=2, capsize=3, capthick=2)

            # fit data to polynomial
            eq_fit = find_poly_reg(heights, y,1)['polynomial'] # Utilities.py
            r2 = find_poly_reg(heights, y,1)['r-squared'] # Utilities.py
            eq_fit_str = 'y= {:.2e}$x$ {:.2e}'.format(np.abs(eq_fit[0]), eq_fit[1])

            sd = np.average(np.abs(np.polyval(eq_fit, heights) - y))
            r2_str = '{:.2f}'.format(r2)
            sd_str = '{:.2e}'.format(sd)

            y_fit  = np.polyval(eq_fit,heights)
            # spl = UnivariateSpline(heights, y) # use scipy spline to auto-fit smooth curve instead of guess-checking polyfit order
            
            # plot fit curve - replace 'y_fit' with 'spl(heights)' to plot smooth curve that connects-the-dots
            ax.plot(heights, y_fit, 
                    #label=r'{}, {}, $R^2$={}, $\Sigma$={}'.format(
                    #    self.rcty_label.capitalize(), eq_fit_str, r2_str, sd_str),
                    color=LINE_COLORS[self.run_type], linestyle=LINE_STYLES[self.run_type], linewidth=LINEWIDTH)
            # ax.legend(ncol=3, loc='upper right')


            try:
                figure_filepath = self.results_folder+f"/{self.base_filename}_{self.run_type}_results_{rho_or_dollars}.png"
                plt.savefig(figure_filepath, bbox_inches = 'tight', pad_inches = 0.1, dpi=320)
            except:
                print(f'\n   fatal. could not save plot to {figure_filepath}')
                print(f'   fatal. you probably have the file open, or that directory does not exist \n')
                sys.exit()