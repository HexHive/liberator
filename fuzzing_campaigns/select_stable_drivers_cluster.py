#!/usr/bin/env python3

import argparse
import os, sys, subprocess
import datetime
from prettytable import PrettyTable

PROJECT_FOLDER="../"
sys.path.append(PROJECT_FOLDER)

import tool.misc.cluster as clst

seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}

def normalize_time_boudget(s):
    return int(s[:-1]) * seconds_per_unit[s[-1]]

def source_bash_file(file_path):
    """Sources a bash file and returns the environment variables."""
    command = f"source {file_path} && env"
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True, executable='/bin/bash')
    output, _ = proc.communicate()
    env_vars = {}
    for line in output.decode().splitlines():
        key, value = line.split('=', 1)
        env_vars[key] = value
    return env_vars

def _main():

    parser = argparse.ArgumentParser(description='Select stable drivers')
    parser.add_argument('-rootdir', '-d', type=str, 
                        help='Driver Folder', required=True)
    parser.add_argument('-gen_time_ratio', '-t', type=float, default=0.5,
                        help='Ratio of tgen to total fuzzing session for selecting the drivers to cluster', required=True)
    parser.add_argument('-simulate', '-s', choices=['full', 'short', 'table'], const='full', nargs='?',
                        help='Simulation only, not moving files around', 
                        required=False)
    parser.add_argument('-keepcorpus', '-k', action='store_true', help='Keep corpus from previous campaign')

    args = parser.parse_args()
    
    rootdir = args.rootdir
    simulate = args.simulate
    keepcorpus = args.keepcorpus
    
    # I do not like this mix'd configuration
    my_conf = source_bash_file("campaign_configuration.sh")
    total_generation_time = normalize_time_boudget(my_conf["TIMEOUT"])
    selecting_gen_time = args.gen_time_ratio * total_generation_time

    best_drivers = {}

    timebudget_per_libary = {}
    n_runs = int(my_conf["ITERATIONS"])
    libraries = my_conf["PROJECTS_STRING"].split(":")
    
    elapsed_time_libraries_iters = {}
    for lib in libraries:
        best_drivers[lib] = {}
        timebudget_per_libary[lib] = {}
        for r in range(1, n_runs+1):
            result_folder = os.path.join(rootdir, "workdir_X_X", lib, f"iter_{r}")

            start_clustering = datetime.datetime.now()
            drivers_for_deep = clst.cluster_drivers(result_folder, selecting_gen_time)
            end_clustering = datetime.datetime.now()

            epalsed_time = end_clustering - start_clustering

            elapsed_time_libraries_iters[f"{lib}_{r}"] = epalsed_time

            deep_fuzzing_time = total_generation_time-selecting_gen_time
            best_drivers[lib][r] = drivers_for_deep
            if len(drivers_for_deep) == 0:
                timebudget_per_libary[lib][r] = f"{deep_fuzzing_time}s"
            else:
                timebudget_per_libary[lib][r] = f"{int(deep_fuzzing_time/len(drivers_for_deep))}s"

    t = None
    if simulate == "table":
        t = PrettyTable(['Library', 'tot. drv.', 'sel. drv', 'avg [s]'])

    if simulate in ["full", "short", "table"]:
        print("[INFO] Only simulation, here the drivers I would select:")
        for lib, drvs in best_drivers.items():
            accumulated_time = 0
            accumulated_drivers = 0
            for r in range(1, n_runs+1):
                tb = timebudget_per_libary[lib][r]
                elapsed_time = elapsed_time_libraries_iters[f'{lib}_{r}']
                if simulate != "table":
                    print(f"{lib} run {r}: {len(drvs[r])} drivers w/ timebudget {tb}, clustering time {elapsed_time}")
                accumulated_time += elapsed_time.total_seconds()
                accumulated_drivers += len(drvs[r])
                if simulate == "full":
                    for driver, api_seq in drvs[r]:
                        # n_drivers = d['n_drivers']
                        # n_apis = d['n_apis']

                        d_path = f"workdir_X_X/{lib}/iter_{r}/drivers/{driver}"
                        print(f"{d_path} {api_seq}")

                    print("-" * 30)
            if simulate == "table":
                t.add_row([lib, len(drvs[r]), int(accumulated_drivers/n_runs), accumulated_time/n_runs])
            else:
                print(f"Average clustering time {accumulated_time/n_runs}")
                print(f"Average drivers {accumulated_drivers/n_runs}")

        if t is not None:
            print(t)

        exit(0)
        
    os.system("mkdir -p workdir_backup")
    os.system("mv workdir_*_*/ workdir_backup")

    # from IPython import embed; embed(); exit(1)

    for lib, all_drvs in best_drivers.items():
        for r in range(1, n_runs+1):
            drvs = all_drvs[r]
            print(f"{lib} {r}: {len(drvs)} drivers")
            for (driver, api_seq) in drvs:

                # cp compiled driver
                os.system(f"mkdir -p workdir_X_X/{lib}/iter_{r}/drivers")
                os.system(f"cp {rootdir}/workdir_X_X/{lib}/iter_{r}/drivers/{driver} workdir_X_X/{lib}/iter_{r}/drivers")

                # cp source code driver
                os.system(f"cp {rootdir}/workdir_X_X/{lib}/iter_{r}/drivers/{driver}.cc workdir_X_X/{lib}/iter_{r}/drivers")

                # cp profile driver
                os.system(f"mkdir -p workdir_X_X/{lib}/iter_{r}/profiles")
                os.system(f"cp {rootdir}/workdir_X_X/{lib}/iter_{r}/profiles/{driver}_profile workdir_X_X/{lib}/iter_{r}/profiles")

                # cp cluster driver
                os.system(f"mkdir -p workdir_X_X/{lib}/iter_{r}/cluster_drivers")
                os.system(f"cp {rootdir}/workdir_X_X/{lib}/iter_{r}/cluster_drivers/{driver}_cluster workdir_X_X/{lib}/iter_{r}/cluster_drivers")

                # cp corpus for driver
                os.system(f"mkdir -p workdir_X_X/{lib}/iter_{r}/corpus")
                
                if keepcorpus:
                    os.system(f"cp -r {rootdir}/workdir_X_X/{lib}/iter_{r}/corpus_new/{driver} workdir_X_X/{lib}/iter_{r}/corpus")
                else:
                    os.system(f"cp -r {rootdir}/workdir_X_X/{lib}/iter_{r}/corpus/{driver} workdir_X_X/{lib}/iter_{r}/corpus")

                # cp metadata for driver
                os.system(f"mkdir -p workdir_X_X/{lib}/iter_{r}/metadata")
                os.system(f"cp -r {rootdir}/workdir_X_X/{lib}/iter_{r}/metadata/{driver}.meta workdir_X_X/{lib}/iter_{r}/metadata")

                # os.system(f"mkdir -p workdir_X_X/{lib}/iter_{r}/corpus_new")
                # os.system(f"cp -r workdir_X_X/{lib}/iter_{r}/corpus_new/{driver} workdir_X_X/{lib}/iter_{r}/corpus_new")

                os.system(f"mkdir -p workdir_X_X/{lib}/iter_{r}/crashes/{driver}")

    # save timebudget per library
    with open("./time_budget.csv", "w") as f:
        for l, t in timebudget_per_libary.items():
            for r in range(1, n_runs + 1):
                f.write(f"{l}|{r}|{t[r]}\n")
                
                
    # save selected drivers per library
    print("[INFO] Storing the selected drivers")
    for lib in libraries:
        for r in range(1, n_runs+1):
            result_folder = os.path.join("workdir_X_X", lib, f"iter_{r}")
            os.makedirs(result_folder, exist_ok=True)
            with open(os.path.join(result_folder, "selected_drivers.txt"), "w") as f:
                for driver_name, api_seq in best_drivers[lib][r]:
                    f.write(f"{driver_name}:{api_seq}\n")
                    
    if os.listdir("workdir_backup") == []:
        os.removedirs("workdir_backup")


if __name__ == "__main__":
    _main()
