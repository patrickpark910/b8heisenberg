# Constants
total_boron_ppm = 3
conversion_factor_ppm_to_fraction = 1e-6

# Natural abundances
abundance_B10 = 0.199
abundance_B11 = 0.801

# Convert ppm to mass fraction for total boron
mass_fraction_boron = total_boron_ppm * conversion_factor_ppm_to_fraction

# Calculate mass fraction of each isotope
mass_fraction_B10 = mass_fraction_boron * abundance_B10
mass_fraction_B11 = mass_fraction_boron * abundance_B11

print(mass_fraction_B10, mass_fraction_B11)