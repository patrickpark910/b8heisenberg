
from MCNP_Input import *
from Utilities import *
from Parameters import *


class Sensitivity(MCNP_File):

    def extract_keff(self):
        """ Parses output file for keff, 1sgima uncertainty, and thermal fission fraction.
        """
        if os.path.exists(self.results_folder):
            try:
                get_keff = False
                get_therm_n_frac = False
                found_keff = False

                with open(self.output_filepath) as f:
                    for line in f:
                        if len(line.split()) > 2 and line.split()[1]=='(<0.625':
                            self.therm_n_frac = float(line.split()[3].replace('%',''))
                            print(f'  | comment. found thermal neutron % = {self.therm_n_frac}')

                        if line.startswith(" the estimated average keffs"):
                            get_keff = True
                        elif get_keff and line.startswith("       col/abs/trk len") and not found_keff:
                            self.keff, self.keff_unc = float(line.split()[2]), float(line.split()[3])
                            found_keff = True
                            print(f'  | comment. found keff: {self.keff} +/- {self.keff_unc}')
            except:
                print(f"\n   warning. keff not found in {self.output_filepath}")
                print(f"   warning.   skipping {self.output_filepath}")
        else:
            print(f'\n   fatal. cannot find {self.results_folder}\n')
            sys.exit(2)

    def process_keff(self):

        self.keff_filename = f'{self.base_filename}-keff.csv'
        self.keff_filepath = f"{self.results_folder}/{self.keff_filename}"

        if self.run_type in ['A']:
            self.index_var, self.index_header, self.index_data = self.fuel_density, 'fuel density (g/cc)', FUEL_DENSITIES
        elif self.run_type in ['B']:
            self.index_var, self.index_header, self.index_data = self.d2o_purity, 'modr purity (mol%)', MODR_PURITIES

        print(f"\n  __MCNP_Output.py")
        self.extract_keff()

        if self.keff_filename in os.listdir(self.results_folder):
            try:
                print(f'  | comment. reading existing results csv: {self.keff_filepath}')
                df_keff = pd.read_csv(self.keff_filepath, encoding='utf8')
                df_keff.set_index(self.index_header, inplace=True)
            except: 
                print(f"\n  | fatal.   cannot read results csv: {self.keff_filename}")
                print(f"  | fatal.   check output processing correct for this run type in process_keff()")
                sys.exit(2)
        else:
            print(f'  | comment. creating new results csv: {self.keff_filepath}')
            df_keff = pd.DataFrame(self.index_data, columns=[self.index_header])
            df_keff.set_index(self.index_header, inplace=True)
             
        df_keff.loc[self.index_var, "keff"] = self.keff
        df_keff.loc[self.index_var, "keff unc"] = self.keff_unc
        df_keff.loc[self.index_var, "therm n %"] = self.therm_n_frac

        # ''' Drop rows if index is not in self.index_data
        # - Necessary if 'fuel_temperatures_C' or 'h2o_tempeartures_C' or 'h2o_void_percents' is redefined in a new run,
        # as this code overwrites existing keff csv instead of creating new file, so old list values will otherwise stay on the df
        # '''
        # for idx in list(df_keff.index.values):
        #     if idx not in self.index_data:
        #         df_keff = df_keff.drop([idx])

        # to put df in increasing order based on the index column, USE inplace=False
        df_keff = df_keff.sort_values(by=self.index_header, ascending=True,inplace=False) 
        df_keff.to_csv(self.keff_filepath, encoding='utf8')
        print(f'  | comment. added mcnp results to csv: {self.keff_filepath}')
