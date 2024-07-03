from MCNP_File import *
from Utilities import *
from Parameters import *


class Geometry(MCNP_File):

    def process_keff(self):

        self.keff_filename = f'{self.base_filename}_keff.csv'
        self.index_var, self.index_header = self.cube_interval, 'cube interval (cm)'

        if self.run_type in ['axial_z']:
            self.index_data = CUBE_INTERVALS
        
        elif self.run_type in ['pack']:
            self.index_var = self.n_cubes_chain_a
            self.index_header = "idx chain a"
            self.index_data = [x[0] for x in CUBE_PACKS]

        elif self.run_type in ['axial_ex','axial_z_ex','axial_z_ex_6']:
            self.index_data = CUBE_INTERVALS_EXTD
            self.keff_filename = f'{self.base_filename}_r{round(self.r_tank)}_{self.n_cubes_chain_a}_{self.n_cubes_chain_b}_keff.csv'
            self.keff_filepath = f"{self.results_folder}/{self.keff_filename}"
        
        elif self.run_type in ['radial_ex']:
            self.index_var, self.index_data, self.index_header = self.r_tank-TANK_RADIUS, RADIAL_INCREASE, "tank radius"

        elif self.run_type in ['J']:
            self.index_var, self.index_data, self.index_header = self.cube_interval, CUBE_INTERVALS_J, 'cube interval (cm)' 
            self.keff_filename = f'{self.base_filename}_r{round(self.r_tank)}_a{self.n_cubes_chain_a}_b{self.n_cubes_chain_b}_keff.csv'
        
        self.keff_filepath = f"{self.results_folder}/{self.keff_filename}"
        # need to make sure self.keff_filepath has latest keff_filename
        
        self.extract_keff()
        print(self.run_type)
        print(self.index_var, self.index_data, self.index_header)
        print(self.keff)

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
             
        df_keff.loc[self.index_var, "tank h cm"] = self.h_tank
        df_keff.loc[self.index_var, "tank r cm"] = self.r_tank
        df_keff.loc[self.index_var, "chain a"] = self.n_cubes_chain_a
        df_keff.loc[self.index_var, "chain b"] = self.n_cubes_chain_b
        df_keff.loc[self.index_var, "cube interval"] = self.cube_interval
        df_keff.loc[self.index_var, "offset"] = self.first_cube_offset
        df_keff.loc[self.index_var, "keff"] = self.keff
        df_keff.loc[self.index_var, "keff unc"] = self.keff_unc
        df_keff.loc[self.index_var, "therm fis %"] = self.therm_n_frac

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



