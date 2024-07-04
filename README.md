<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a id="readme-top"></a>

<!-- PROJECT LOGO -->
<br />
<h3 align="center">Nuclear Forensics of the B8: Heisenberg's Last Reactor</h3>

  <p align="center">
    This repository has all the code and data in support of our paper.
    <br />
    <a href="https://github.com/github_username/repo_name"><strong>Explore the docs »</strong></a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- GETTING STARTED -->
## Getting Started

This is an example of how you may give instructions on setting up your project locally.
To get a local copy up and running follow these simple example steps.

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.
* npm
  ```sh
  npm install npm@latest -g
  ```

### Installation

1. Get a free API Key at [https://example.com](https://example.com)
2. Clone the repo
   ```sh
   git clone https://github.com/github_username/repo_name.git
   ```
3. Install NPM packages
   ```sh
   npm install
   ```
4. Enter your API in `config.js`
   ```js
   const API_KEY = 'ENTER YOUR API';
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>


# Code & Data Processing Walkthrough

In this section, I'll describe what my (often Python-scripted) MCNP inputs do and how I processed the MCNP outputs to obtain the data I got. I'll go folder-by-folder.

## B8 Fiducial - Flux

### MCNP Input File: 
[`b8_caseR_rings5_d2o96-8_RaBe.inp`](</B8 Fiducial - Flux/b8_caseR_rings5_d2o96-8_RaBe.inp>)

The following `SDEF` card defines a Radon-Beryllium source. It is modeled as a point source, located at `(0, 0, 62)` of the MCNP model (center of the B8). It has a distribution of emitted neutron energies `d1` defined by the energy bins in MeV in `si1` and the probability of each bin in `sp1`, e.g., no neutrons < 0.316 MeV, 0.347% between 0.316 MeV to 0.398 MeV, etc. This data is from the [IAEA <i>Compendium of Neutron Spectra</i> (1990), p.79](inis.iaea.org/collection/NCLCollectionStore/_Public/21/092/21092101.pdf). 
```
sdef  pos= 0 0 62  erg=d1  par=n
si1  0.316   0.398   0.501   0.631   0.794   1.00    1.26
     1.58    2.00    2.51    3.16    3.98    5.01    6.31
     7.94   10.0    12.6 
sp1     0    3.47e-3 2.66e-3 1.65e-3 2.03e-3 1.06e-2 2.75e-2 
     5.19e-2 6.55e-2 7.31e-2 9.95e-2 1.64e-1 1.78e-1 1.21e-1
     1.41e-1 5.71e-2 1.39e-3 
```

Having defined our RaBe source, this `F4` tally card meaures the volume flux per source neutron in the heavy water (material `1100`) + all the fuel cubes (mats `2001`-`6024`).
```
fc14 n flux in hwtr + fuel
f14:n (1100 2001 2002 2003 2004
            ...
            6023 6024)
```

This `NPS` card states we will run the calculation with `1e6` source neutrons emitted from our RaBe source. The `F4` tally normalizes results to be per 1 source neutron anyways, so bigger the `NPS` the better fidelity. Then, you can manually scale your flux to the real number of neutrons being emitted by the RaBe source per second, if you know its activity (which we do not for the B8).
```
nps 1e6
```

This `KCODE` card calculates $k_\text{eff}$ with 200,000 source neutrons (this time the source of neutrons being the coordinates of the centers of each fuel cube in `KSRC`), 115 active cycles, and 15 discarded cycles (giving time for the neutron population to converge). I commented it out (`c`) because I had calculated $k_\text{eff}$ in Case R of the other B8 Fiducial folder, but you can also uncomment this and run it yourself.
```
c kcode 200000 1 15 115
```

### MCNP Output File: 
[`o_b8_caseR_rings5_d2o96-8_RaBe.o`](</B8 Fiducial - Flux/o_b8_caseR_rings5_d2o96-8_RaBe.o>)

The `F4` tally results can be found by searching for "`1tally       14`":
```
1tally       14        nps =     1000000
+                                   n flux in hwtr + fuel                                                      
           tally type 4    track length estimate of particle flux.      units   1/cm**2        
           particle(s): neutrons 
           cell  a is (1100 2001 2002 [...] 6024)                                                                                                             

           volumes 
                   cell:        a                                                                                  
                         1.48300E+06
 
 cell (1100 2001 2002 [...] 6023 6024)                                                                   
      energy   
    1.0000E-09   7.96402E-07 0.0029
    1.0267E-09   4.22215E-08 0.0049
    1.0541E-09   4.44174E-08 0.0049
    1.0822E-09   4.71006E-08 0.0048
    [...]
    1.9480E+01   9.35945E-11 0.2124
    2.0000E+01   8.17292E-11 0.2549
      total      2.26368E-03 0.0027
```

We have energy bins, the neutron flux tallied within each energy range, and the error. We just copy this into a `.csv` and plot it in Excel (or Python matplotlib).

## B8 Fiducial - k_eff - Sensitivty Analyses

This is where understanding my code gets a little tricky, because I wrote a huge Python wrapper to automate writing + processing MCNP for me. I don't think anyone will really use my code anyways, but I'll write it out just as due diligence.

Here's the folders in this directory:
- [./Figures/](</B8 Fiducial - k_eff - Sensitivity/Figures>) - For data processing. I don't have any scripts that touch this folder.
- [./MCNP/](</B8 Fiducial - k_eff - Sensitivity/MCNP>) - Where my Python wrapper writes MCNP inputs and stores MCNP outputs + the `temp`orary directory for when MCNP is actively writing. You should not have to touch anything in here unless MCNP throws an error, in which case you need to go in and manually delete the erroneous input or output (failsafe to prevent any unintentional overwrites).
- [./Results/](</B8 Fiducial - k_eff - Sensitivity/Results>) - Where the CSVs collating results get written.
- [./Source/](</B8 Fiducial - k_eff - Sensitivity/Source>) - Where my Python wrapper scripts and MCNP templates are kept. If you just want to replicate my data exactly, you shouldn't need to touch this folder. If you want to tweak certain parts of my sensitivity analysis, e.g., test criticality at an even lower moderator purity, then you only need to touch `Parameters.py`

I'll now try to walk through executing my code and what happens under the hood.

### Executing the Python Wrapper

Ideally, executing this all is relatively simple (duh, that's the point of scripting everything, except for the 7,621 times it breaks!). In your terminal, `cd` to this directory and use:
```
python B8Analysis.py -r <run_type> -t <tasks>
```

You have three options for `<run_type>` or 'cases':

- `A`: perturb U cube density
- `B`: perturb D2O mol% purity (remainder as H2O)
- `J`: I have legacy data about case J where I elongate the cubes of chains from (9 + 8) to (10 + 9).
- `R`: reference fiducial cases 

(When I was really deep in the trenches, I actually had `A` through `S`)

The `<tasks>` is the number of logical processors you have on your computer. You can leave the `-t` argument empty, and `B8Analysis.py` will check how many you have for you.

Let's say we want to perturb the U cube density, so we use `run_type = A`, and I have 32 logical processors :
```
python B8Analysis.py -r A -t 32
```



### What the Wrapper Does: Front-End

**Step 1**

Now that we've executed run type `A`, from `B8Analysis.py`, we then read the `FUEL_DENSITIES` we want to test from `Parameters.py`. 

```py
elif run_type == 'A':
    for fuel_density in FUEL_DENSITIES:
      current_run = Sensitivity(run_type,
                                tasks,
                                print_input=check_mcnp,
                                fuel_density=fuel_density)
```

This then populates the `Sensitivity` class in `MCNP_Output.py`:
```py
class Sensitivity(MCNP_File):
```
which has a `MCNP_File` class defined in `MCNP_Input.py`:
```py
class MCNP_File:
    def __init__(self,run_type,tasks,
               print_input=True, 
               delete_extensions=['.s'],  # default: '.s'
               r_tank=TANK_RADIUS, #  61.7 cm
               h_tank=TANK_HEIGHT, # 124.0 cm
               n_rings=5,
               [...] )
```

**Step 2**

`MCNP_Input.py` is where the bulk of the scripting occurs. In the `MCNP_File` class, we first define, calculate, etc. all of the necessary physical parameters. To do so, I also call several helper functions from `Utilities.py`. For example, we calculate the D2O density to program into the MCNP input, using the helper `d2o_temp_K_to_mass_density(d2o_temp_K)`:

```py
self.d2o_density = (1-0.01*self.d2o_void_percent)*d2o_temp_K_to_mass_density(d2o_temp_K)
```

where we set `d2o_temp_K` to the  B8's ambient 11 C (`AMBIENT_TEMP_K = 284` in `Parameters.py`).  

**Step 3**

Then, we use the physical constants to write code chunks in MCNP syntax. For instance, we need to call the necessary cross section libraries for particle transport in the moderator. Like described in the paper, we want to perform temperature interpolation. So in `MCNP_Input.py` we run the function `find_xs_libs()`:

```py
def find_xs_libs(self):
  self.d2o_mats_interpolated_str = wtr_interpolate_mat(self.d2o_temp_K, d2o_atom_percent=self.d2o_purity)
```

which calls `wtr_interpolate_mat()` from `Utilities.py`:

```py
def wtr_interpolate_mat(temp_K, d2o_atom_percent=0):
  [...]
  return wtr_mats_interpolated
```

```py
>>> wtr_interpolate_mat(294, d2o_atom_percent=100)
"1002.00c  2.00  8016.00c 1.00"
>>> wtr_interpolate_mat(294, d2o_atom_percent=50)
"1001.00c  1.00      1002.00c  1.00      8016.00c 1.00"
>>> wtr_interpolate_mat(284, d2o_atom_percent=96.8)
"1001.06c 0.014100  1001.00c 0.049900    1002.06c 0.426529  1002.00c 1.509471    8016.00c 1.00"
```

**Step 4**

We also create the names of our MCNP input and outputs so that its parameters are self-evident from the file name. To avoid any processing issues, we replace any decimals with an underscore `_`.

```py
self.base_filename = f"{self.template_filepath.split('/')[-1].split('.')[0]}-case{self.run_type}"
if self.run_type in ['A','B']:
            self.input_filename = f"{self.base_filename}-d2o{'{:.1f}'.format(self.d2o_purity).replace('.','_')}-Urho{'{:.2f}'.format(self.fuel_density).replace('.','_')}.inp"
self.output_filename = f"o_{self.input_filename.split('.')[0]}.out"
```

Some examples of `self.input_filename` and `self.output_filename` are:
```
b8-caseA-d2o96_8-Urho15_00.inp
b8-caseA-d2o96_8-Urho19_25.inp
b8-caseB-d2o85_0-Urho18_53.inp
b8-caseB-d2o100_0-Urho18_53.inp

o_b8-caseA-d2o96_8-Urho15_00.out
o_b8-caseA-d2o96_8-Urho19_25.out
o_b8-caseB-d2o85_0-Urho18_53.out
o_b8-caseB-d2o100_0-Urho18_53.out
```

We can read that case `A` keeps the moderator purity constant at the reference 96.8 mol% D2O while changing the fuel density, and vice versa for case `B`, just as God (yours truly) intended.

**Step 5**

Once we do that, we load everything into a dictionary `self.parameters`:
```py
self.parameters = {'datetime': self.datetime,
                   'run_type': self.run_type,
                   'r_tank' : self.r_tank,
                   'h_tank' : self.h_tank,
                   'n_rings': self.n_rings,
                   [...]
                   'h_h2o_sab_lib': self.h_h2o_sab_lib,
                   'd_d2o_sab_lib': self.d_d2o_sab_lib,}
```

 it into the `b8.template` MCNP input template using the `Jinja2` package:

```py
if self.print_input:
    with open(self.template_filepath, 'r') as template_file:
        template_str = template_file.read()
        template = Template(template_str)
        template.stream(**self.parameters).dump(self.input_filepath)
```


**Step 6**

Now that the MCNP input file is written, we then run MCNP:
```py
def run_mcnp(self):
    if self.output_filename not in os.listdir(self.outputs_folder):
        cmd = f"""mcnp6 i="{self.input_filepath}" n="{self.user_temp_folder}/{self.output_filename.split('.')[0]}." tasks {self.tasks}"""
        os.system(cmd)
        self.mcnp_skipped = False
    else:
        self.mcnp_skipped = True
```

Notice that MCNP is writing outputs to a temporary `./MCNP/<run_type>/temp/` folder. After MCNP finishes, we then move the outputs to `./MCNP/<run_type>/outputs/` folder with `move_mcnp_files()` in `MCNP_Input.py`.

### What the Wrapper Does: Back-End


<p align="right">(<a href="#readme-top">back to top</a>)</p>





See the [open issues](https://github.com/github_username/repo_name/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Your Name - [@twitter_handle](https://twitter.com/twitter_handle) - email@email_client.com

Project Link: [https://github.com/github_username/repo_name](https://github.com/github_username/repo_name)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* []()
* []()
* []()

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/github_username/repo_name.svg?style=for-the-badge
[contributors-url]: https://github.com/github_username/repo_name/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/github_username/repo_name.svg?style=for-the-badge
[forks-url]: https://github.com/github_username/repo_name/network/members
[stars-shield]: https://img.shields.io/github/stars/github_username/repo_name.svg?style=for-the-badge
[stars-url]: https://github.com/github_username/repo_name/stargazers
[issues-shield]: https://img.shields.io/github/issues/github_username/repo_name.svg?style=for-the-badge
[issues-url]: https://github.com/github_username/repo_name/issues
[license-shield]: https://img.shields.io/github/license/github_username/repo_name.svg?style=for-the-badge
[license-url]: https://github.com/github_username/repo_name/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/linkedin_username
[product-screenshot]: images/screenshot.png
[Next.js]: https://img.shields.io/badge/next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white
[Next-url]: https://nextjs.org/
[React.js]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
[React-url]: https://reactjs.org/
[Vue.js]: https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D
[Vue-url]: https://vuejs.org/
[Angular.io]: https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white
[Angular-url]: https://angular.io/
[Svelte.dev]: https://img.shields.io/badge/Svelte-4A4A55?style=for-the-badge&logo=svelte&logoColor=FF3E00
[Svelte-url]: https://svelte.dev/
[Laravel.com]: https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white
[Laravel-url]: https://laravel.com
[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[JQuery.com]: https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white
[JQuery-url]: https://jquery.com 