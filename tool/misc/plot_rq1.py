#!/usr/bin/env python3
from scipy.interpolate import make_interp_spline, BSpline
import numpy as np
import matplotlib.lines as lines
import matplotlib.text as text
import matplotlib.pyplot as plt
import matplotlib as mpl
import csv
try:
    font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 30}

    mpl.rc('font', **font)
    mpl.rcParams['text.usetex'] = True
    mpl.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}'
except:
    print("[INFO] LaTeX not detected, keep going without")
    pass
import argparse
import os
parser = argparse.ArgumentParser(description='Plotting script')
parser.add_argument('--interval', '-i', type=int, default=3,
                    help='Number of tgen/ttest config - 1')
parser.add_argument('--folder', '-d', type=str,
                    help='Campaign folder', required=True)
parser.add_argument('--timeout', '-t', type=str, default='24h',
                    help='TIMEOUT enivronment variable')
args = parser.parse_args()

# Data
timeout_no_unit = int(args.timeout[:-1])
ratio = [args.timeout] + [ str(int(timeout_no_unit - i*timeout_no_unit/(1+args.interval))) + args.timeout[-1] for i in range(1, args.interval+1)]

generations = list(map(lambda x: r"\textbf{"+x+"}", ratio))
generations.reverse() 
data = {}

# get the argument from the command line

for r in ratio:
    campaign_name = "gen" + r[:-1] + "_deep" + str(timeout_no_unit - int(r[:-1]))

    with open(os.path.join(args.folder, campaign_name,  "total_library_coverage.csv"), "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] not in data:
                data[row[0]] = []
            print(row)
            data[row[0]].append(0 if len(row[1]) < 2 else float(row[1][:-1]))

#data["c_ares"] = [55.29, 50.88, 49.06, 52.65]
#data["cjson"] = [75.34, 73.20, 71.52, 72.68]
#data["libaom"] = [10.98, 10.57, 5.51, 11.77]
#data["libhtp"] = [26.74, 25.07, 16.34, 17.37]
#data["libpcap"] = [40.93, 40.81, 37.48, 38.03]
#data["libtiff"] = [24.45, 26.93, 27.70, 26.36]
#data["libvpx"] = [8.24, 8.90, 3.71, 7.59]
#data["minijail"] = [18.45, 15.48, 16.03, 16.07]
#data["cpufeatures"] = [19.22, 19.22, 19.22, 19.22]
#data["pthreadpool"] = [50.44, 44.21, 36.42, 40.42]
#data["zlib"] = [58.32, 58.83, 46.26, 55.01]
#data["libdwarf"] = [18.08, 17.88, 17.89, 17.89]
#data["libplist"] = [54.30, 54.43, 53.97, 51.13]
#data["libsndfile"] = [26.50, 31.75, 35.46, 36.59]
#data["libucl"] = [56.34, 57.02, 57.43, 57.78]



# Plotting
fig, ax = plt.subplots(figsize=(13, 9.7))

l = ['solid', 'dotted']
colors = ['b', 'g', 'r', 'c', 'm', 'k', 'peru']
markers = ['o', 'X', '*']
xnew = np.linspace(6, 24, 300)  
i = 0
for(lib, values) in data.items():
    values.reverse()
    values = values / np.max(values) * 100
    ax.plot(generations, values, label=r"\texttt{"+lib+r"}", marker=markers[i%3], linestyle=l[i%2], color=colors[i%7], markersize=8, linewidth=3)
    i += 1

# Labels and Title
#ax.set_ylim(ymin=0)
fig.subplots_adjust(top=0.8, left=0.12, bottom=0.27, right=0.98)
plt.xlabel(r"$\bf{t_{gen}}$")
plt.ylabel(r'\textbf{Normalized Coverage [\%]}')
fig.canvas.draw()
labels = [item.get_text() for item in ax.get_yticklabels()]
m = map(lambda x: x.replace("default", "bf"), labels)
ax.set_yticklabels(list(m))
plt.legend(bbox_to_anchor=(-0.05, -0.2), markerscale=1.3, loc='upper left', fontsize=25, labelspacing=0.015, borderpad=0.2, handlelength=1.5, handletextpad=0.1, columnspacing=0.2, ncol=5)

# Show plot
fig.add_artist(lines.Line2D([0.22,0.87], [0.9, 0.9], color='black', linewidth=2, marker='<', markersize=12, markevery=2))
fig.add_artist(lines.Line2D([0.87,0.22], [0.9, 0.9], color='black', linewidth=2, marker='>', markersize=12, markevery=2))
fig.add_artist(text.Text(0.71, 0.94, r"\textbf{more drivers}"), )
fig.add_artist(text.Text(0.11, 0.94, r"\textbf{less drivers}"), )
fig.add_artist(text.Text(0.71, 0.84, r"\textbf{less testing}"), )
fig.add_artist(text.Text(0.11, 0.84, r"\textbf{more testing}"), )
# plt.savefig('fig3.png')
plt.savefig('fig3.pdf')
# plt.show()
