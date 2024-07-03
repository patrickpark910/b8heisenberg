import numpy as np
from MCNP_Input import *
from Utilities import *
from Parameters import *


class Cylinder(MCNP_Input):

    def process_keff(self):

        self.keff_filename = f'{self.base_filename}-keff.csv'

        if self.run_type in ['SC']:
            self.keff_filename = f'{self.base_filename}-keff.csv'
            self.keff_filepath = f"{self.results_folder}/{self.keff_filename}"
            self.index_var = self.output_filename
            self.index_header = "output_filename"
            self.index_data = []
            for n in SC_N_CUBES: # SD_N_CUBES:
                for m in SC_MODR_VOLS:
                    V = n*CUBE_LENGTH**3 + m
                    r = (V/2/np.pi)**(1/3) 
                    # use append not += concactenation
                    self.index_data.append(f"o_{self.base_filename}-c{n}-r{'{:.2f}'.format(r).replace('.','_')}-d2o{'{:.1f}'.format(self.d2o_purity).replace('.','_')}-v{round(m/1e3)}.o")


        self.keff_filepath = f"{self.results_folder}/{self.keff_filename}"
        # need to make sure self.keff_filepath has latest keff_filename
        
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
          
        df_keff.loc[self.index_var, "cubes"] = rd(self.n_cubes)
        df_keff.loc[self.index_var, "modr v L"] = rd(self.modr_vol/1e3)
        df_keff.loc[self.index_var, "core r cm"] = rd(self.r_core)
        df_keff.loc[self.index_var, "keff"] = self.keff
        df_keff.loc[self.index_var, "keff unc"] = self.keff_unc
        df_keff.loc[self.index_var, "therm fis %"] = self.therm_n_frac

        ''' Drop rows if index is not in self.index_data
        - Necessary if 'fuel_temperatures_C' or 'h2o_temperatures_C' or 'h2o_void_percents' is redefined in a new run,
        as this code overwrites existing keff csv instead of creating new file, so old list values will otherwise stay on the df

        for idx in list(df_keff.index.values):
            if idx not in self.index_data:
                df_keff = df_keff.drop([idx])
        '''
        
        # to put df in increasing order based on the index column, USE inplace=False
        df_keff = df_keff.sort_values(by=self.index_header, ascending=True,inplace=False) 
        df_keff.to_csv(self.keff_filepath, encoding='utf8')
        





