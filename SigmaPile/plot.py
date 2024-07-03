import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

# Read the big CSV file
df = pd.read_csv('plotdata.csv')

x = df.iloc[:, 0]
th_spline = make_interp_spline(x, df.iloc[:, 1])
if_spline = make_interp_spline(x, df.iloc[:, 2])
ab_spline = make_interp_spline(x, df.iloc[:, 3])
 
# Returns evenly spaced numbers over a specified interval.
x_ = np.linspace(x.min(), x.max(), 500)
th_ = th_spline(x_)
if_ = if_spline(x_)
ab_ = ab_spline(x_)
print(x_[222:225], th_[222:225])
print(np.amax(th_))

# Create a figure and axis
fig, ax = plt.subplots(figsize=(4, 3))

#
ax.plot(x, df.iloc[:, 1], 
	label='th', linewidth=0, color="red", marker='+'
	) # 
ax.plot(x, df.iloc[:, 2], 
	label='int+f', linewidth=0, color="black", marker='.'
	)
ax.plot(x, df.iloc[:, 3], 
	label='abs', linewidth=0, color="blue", marker='x'
	)

# Plot the data from each column
ax.plot(x_, th_, 
	label='th', linewidth=1, color="red", 
	) # marker='+'
ax.plot(x_, if_, 
	label='int+f', linewidth=1, color="black", #marker='.'
	)
ax.plot(x_, ab_, 
	label='abs', linewidth=1, color="blue", # marker='x'
	)

# Add labels and legend
# Set the font size for various elements
ax.set_xticks(range(0, int(df.iloc[:, 0].max()) + 5, 5))
ax.set_yticks(np.arange(0, 1.01, 0.2))
ax.set_ylim(0, 1.0)
ax.set_xlim(left=0)
ax.set_xlim(right=40)
ax.set_ylim(bottom=0)

# Add labels and legend
ax.set_xlabel('Depth [cm]', fontname='Arial')
ax.set_ylabel('Fraction of Neutrons', fontname='Arial')


# ax.set_title('Plot Title', fontname='Arial')

# Set the font of the tick labels to Arial
for tick in ax.get_xticklabels() + ax.get_yticklabels():
    tick.set_fontname('Arial')
plt.rcParams.update({'font.size': 36})

# ax.legend(prop={'family': 'Arial'})

# Display the plot
plt.savefig("test.svg", transparent=True, bbox_inches='tight',pad_inches=0, format="svg")
plt.show()