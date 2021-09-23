
from MCNP_File import *
from Utilities import *
from Parameters import *


class BaseCase(MCNP_File):
    def process_base_keff(self):
        pass

class DensityFuel(MCNP_File):

    def process_dens_fuel_keff(self):

        self.keff_filename = f'{self.base_filename}_{self.run_type}_keff.csv'
        self.keff_filepath = f"{self.results_folder}/{self.keff_filename}"

        self.index_var, self.index_header, self.index_data = self.fuel_density, 'mass density (g/cc)', FUEL_DENSITIES

        self.extract_keff()

        if self.keff_filename in os.listdir(self.results_folder):
            try:
                df_keff = pd.read_csv(self.keff_filepath, encoding='utf8')
                df_keff.set_index(self.index_header, inplace=True)
            except:
                print(f"\n   fatal. Cannot read {self.keff_filename}")
                print(f"   fatal.   Ensure that:")
                print(f"   fatal.     - the file is a .csv")
                print(f"   fatal.     - the first column header is 'height (%)', followed by rod names 'safe', 'shim', 'reg'")
                sys.exit(2)
        else:
            print(f'\n   comment. creating new results file {self.keff_filepath}')
            df_keff = pd.DataFrame(self.index_data, columns=[self.index_header])
            df_keff.set_index(self.index_header, inplace=True)
             
        df_keff.loc[self.index_var, "keff"] = self.keff
        df_keff.loc[self.index_var, "keff unc"] = self.keff_unc
        df_keff.loc[self.index_var, "therm n %"] = self.therm_n_frac

        ''' Drop rows if index is not in self.index_data
        - Necessary if 'fuel_temperatures_C' or 'h2o_tempeartures_C' or 'h2o_void_percents' is redefined in a new run,
        as this code overwrites existing keff csv instead of creating new file, so old list values will otherwise stay on the df
        '''
        for idx in list(df_keff.index.values):
            if idx not in self.index_data:
                df_keff = df_keff.drop([idx])

        # to put df in increasing order based on the index column, USE inplace=False
        df_keff = df_keff.sort_values(by=self.index_header, ascending=True,inplace=False) 
        df_keff.to_csv(self.keff_filepath, encoding='utf8')
