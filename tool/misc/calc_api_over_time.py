#!/usr/bin/env python3

import os, json, argparse
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MaxNLocator
label_font = 38
#plt.rcParams.update({'font.size': label_font})
print(plt.rcParams.get('font.size'))
tot_api = {
    "c-ares": 126,
    "cjson": 78,
    "cpu_features": 7,
    "libaom": 47,
    "libhtp": 251,
    "libpcap": 88,
    'libtiff': 197,
    "libvpx": 35,
    "minijail": 97,
    "pthreadpool": 30,
    "zlib": 88,
    "libdwarf": 333,
    "libplist": 101,
    "libsndfile": 40,
    "libucl": 125
}

def get_runs(rootdir, is_grammar):
    
    if is_grammar:
        return len(os.listdir(rootdir))
    
    raise Exception("get_runs w/o is_grammar not implemented yet")

def read_drivers_metadata(d):
    
    driver_meta = {}
    
    for l in os.listdir(os.path.join(d, "metadata")):
        if l.endswith(".meta"):
            with open(os.path.join(d, "metadata", l), "r") as f:
                md = json.load(f)
            driver_meta[l.replace(".meta", "")] = md
            
    return driver_meta

def read_paths_observed(d, only_positive=False):
    
    paths_observed = []
    
    with open(os.path.join(d, "paths_observed.txt")) as f:
        for l in f:
            if l:
                la = l.split(":")
                driver = la[0]
                apis = set(la[1].split(";"))
                status = la[2]
                n_seeds = int(la[3])
                if not only_positive or (status == "POSITIVE" and n_seeds > 1): 
                    paths_observed += [{"driver": driver,
                                        "apis": apis, 
                                        "status": status, 
                                        "n_seed": n_seeds}]
        
    return paths_observed                
                

def _main():
    
    parser = argparse.ArgumentParser(description='APIs used over time')
    parser.add_argument('-root', '-r', type=str, help='Root folder', required=True, default="/media/hdd0/libfuzz_scratchpad/main/fuzzing_campaigns")
    parser.add_argument('-p', action='store_true', help='Only positive')
    
    args = parser.parse_args()
    
    root_folder = args.root
    
    print(root_folder)
    
    # drivers_metadata = read_drivers_metadata(root_folder)
   
    factor = 4
    size = (4,3)
    #f = plt.figure(figsize=(size[0]*factor, size[1]*factor))
    #gs = gridspec.GridSpec(factor * size[1], factor * size[0])
    #ax =[0]*12
    #for i in range(0,11):
    #    
    #    x_ax = i//size[0]
    #    y_ax = i%size[0]
    #    shift = 0 if x_ax != size[1]-1 else 0.5
    #    ax[i] = f.add_subplot(gs[factor * x_ax: factor*(x_ax+1), int((shift +  y_ax)*factor): int((shift + y_ax + 1)*factor)])
    #f.set_tight_layout(True)
    plot_index = 0
    for t, max in tot_api.items():
        print(t)
        iterations = get_runs(os.path.join(root_folder, t), True)
        x = [0] * iterations
        y = [0] * iterations
        for iter in range(0, iterations): 
            root_folder_p = os.path.join(root_folder, t, "iter_" + str(iter+1))
        
            paths_observed = read_paths_observed(root_folder_p, only_positive=args.p)
        
            # print(paths_observed)
            # exit(1)
        
            # from IPython import embed; embed(); exit(1)
        
            n_api_acc = set()
        
            x[iter] = []
            y[iter] = []    
            for i, d in enumerate(paths_observed):
                n_api_acc |= d["apis"]
                # print(len(n_api_acc))
                x[iter] += [i]
                y[iter] += [len(n_api_acc)]
            
        stop = False
        new_max = 0
        newx = []
        idx = 0
        for i in range(0, iterations):
            if len(x[i]) > new_max:
                new_max = len(x[i])
                newx = x[i]
        newy = [0]*new_max
        last = [0]*iterations
        while not stop:
            stop = True
            for i in range(0, iterations):
                if idx < len(x[i]):
                    last[i] =  y[i][idx]
            
                    stop = False
            if not stop:
                newy[idx] = sum(last)/iterations/max*100
            idx += 1
        plt.cla()
        plt.figure(figsize=(10, 6))

        plt.plot(newx, newy, label='APIs used over time', color='blue')    

        #plt.title("\\texttt{" + t+ "}")
        plt.xlabel('# of drivers', fontsize=label_font)
        if t == "minijail" or t == "libdwarf" or t == "libsndfile" or t == "c-ares":
            plt.ylabel('% of API functions', fontsize=label_font)
        plt.ylim(top=102)
        plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=5))
        plt.yticks([0,50,100], fontsize=label_font)
        plt.xticks(fontsize=label_font)

        plt.grid(True, color='lightgray', linestyle='-', linewidth=0.5)
        plt.tight_layout()
        plt.savefig(f"api_over_time_{t}.pdf", format='pdf')

        #ax[plot_index].plot(newx, newy, label='APIs used over time')    
        #ax[plot_index].set_title("\\texttt{" + t+ "}")
        #ax[plot_index].set_xlabel('\# of drivers')
        #ax[plot_index].set_ylabel('Percentage of API functions reached')
        #ax[plot_index].set_ylim(bottom=0, top=105)
        #ax[plot_index].set_lim(xmin=0)
        #ax[pp].legend()



        plot_index += 1
    #f.suptitle('This is a somewhat long figure title', fontsize=16)
    #plt.savefig(f"api_over_time.pdf", format='pdf')
        
    
if __name__ == "__main__":
    _main()
