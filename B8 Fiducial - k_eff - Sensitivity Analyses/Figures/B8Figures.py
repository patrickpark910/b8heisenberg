import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.colors as colors
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, AutoMinorLocator
# import scienceplots


radii = [61.7,64,66,68,70,72,74,76,78,80,82,84,86]
cubeint = [5.5,6.0,6.5,7.0,7.5,8.0,8.5,9.0,9.5,10.0,10.5,11.0,11.5,12.0,12.5,13.0,13.5,14.0,14.5,15.0,15.5,16.0,16.5,17.0]
markers = {61.7:'.',64:'+',66:'x',68:'1',70:'2',72:'3',74:'4',76:'.',78:'.',80:'.',82:'.',84:'.',86:'.'}

df = pd.read_csv("B8FigureData.csv",index_col=0)
fig, ax = plt.subplots()

radii.reverse()
for r in radii:
    k_list = df[f"{r}"].dropna().tolist()
    ci = []
    for c in cubeint:
        try:
            if not np.isnan(df.loc[c,str(r)]):
                ci.append(c)
        except KeyError:
            pass
        except:
            print(f"oopsie woopsie")
    
    a,b,c = np.polyfit(ci,k_list,2)
    x = np.linspace(ci[0],ci[-1],100)

    plt.scatter(ci,k_list,marker=markers[r],label=f"{r} cm")
    plt.errorbar(x, a*x**2+b*x+c, linewidth=1) #,dashes=(5,2,1,2)) #, label=r)


FONT = 'Times New Roman' # serif, sans-serif, Arial, Comic Sans MS
FONTSIZE = 11
mpl.rc('font',family=FONT) # only changes legend font
ax.set_ylabel(r'Eff. mult. factor [$\mathit{k}_{\mathrm{eff}}$]', fontsize=FONTSIZE, fontfamily=FONT, math_fontfamily='cm')
ax.set_xlabel(r'Cube interval [cm]', fontsize=FONTSIZE, fontfamily=FONT)

ax.xaxis.set_major_locator(MultipleLocator(1))
ax.xaxis.set_minor_locator(MultipleLocator(0.5))
ax.yaxis.set_major_locator(MultipleLocator(0.005))
ax.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))
ax.yaxis.set_minor_locator(AutoMinorLocator(2))

plt.xticks(fontfamily=FONT, fontsize=FONTSIZE)
plt.yticks(fontfamily=FONT, fontsize=FONTSIZE)
ax.tick_params(axis='both', which='major', length=5, direction='in', bottom=True, top=True, left=True, right=True)
ax.tick_params(axis='both', which='minor', length=3.5, direction='in', bottom=True, top=True, left=True, right=True)
ax.legend(ncol=1,loc='lower right')

plt.savefig("test.svg", format="svg",bbox_inches='tight',pad_inches=0.01) # if savefig after show(), it will be blank white
plt.savefig("test.png", format="png",bbox_inches='tight',pad_inches=0.01) # if savefig after show(), it will be blank white
plt.show()

''' Check what fonts available for mpl 

import matplotlib.font_manager
fpaths = matplotlib.font_manager.findSystemFonts()
for i in fpaths:
    f = matplotlib.font_manager.get_font(i)
    # print(f.family_name)
'''

