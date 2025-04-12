#!/usr/bin/env python3

import argparse
import os, sys, subprocess

PROJECT_FOLDER="../"
sys.path.append(PROJECT_FOLDER)

import tool.misc.cluster as clst
from datetime import datetime, timedelta

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
    parser.add_argument('-simulate', '-s', choices=['full', 'short'], const='full', nargs='?',
                        help='Simulation only, not moving files around', 
                        required=False)
    # parser.add_argument('-keepcorpus', '-k', action='store_true', help='Keep corpus from previous campaign')

    args = parser.parse_args()
    
    rootdir = args.rootdir
    simulate = args.simulate
    # keepcorpus = args.keepcorpus
    
    # # I do not like this mix'd configuration
    my_conf = source_bash_file("campaign_configuration.sh")
    total_generation_time = normalize_time_boudget(my_conf["TIMEOUT"])
    selecting_gen_time = total_generation_time * args.gen_time_ratio
    time_window = timedelta(seconds=selecting_gen_time)
    n_runs = int(my_conf["ITERATIONS"])
    libraries = my_conf["PROJECTS_STRING"].split(":")
    
    drivers_to_keep = {}
    for lib in libraries:
        drivers_to_keep[lib] = {}
        for r in range(1, n_runs+1):
            result_folder = os.path.join(rootdir, "workdir_X_X", lib, f"iter_{r}", "drivers")
            
            deep_folder = os.path.join("workdir_X_X", lib, f"iter_{r}")
            
            # drivers_for_deep = clst.cluster_drivers(host_result_folder)
            drivers_for_deep = []
            print(f"[INFO] Retrieving the selected drivers for {lib} {r}")
            with open(os.path.join(deep_folder, "selected_drivers.txt"), "r") as f:
                for l in f:
                    driver_name, _ = l.split(":")
                    drivers_for_deep += [driver_name]
                    
            creation_time_driver0 = clst.get_creation_time(os.path.join(result_folder, "driver0.cc"))
            driver0_creation_datetime = datetime.fromtimestamp(creation_time_driver0)
            
            
            drivers_to_keep[lib][r] = []
            for driver in os.listdir(result_folder):
                if driver.endswith(".cc"):
                    continue
            
                if driver in drivers_for_deep:
                    continue
                
                driver_path = os.path.join(result_folder, f"{driver}.cc")
                driver_creation_time = clst.get_creation_time(driver_path)
                driver_creation_datetime = datetime.fromtimestamp(driver_creation_time)
                
                if driver_creation_datetime - driver0_creation_datetime >= time_window:
                    continue
                    
                drivers_to_keep[lib][r] += [driver]
            # drivers_for_deep = clst.cluster_drivers(result_folder, selecting_gen_time)
            # deep_fuzzing_time = total_generation_time-selecting_gen_time
            # best_drivers[lib][r] = drivers_for_deep
            # if len(drivers_for_deep) ==0 :
            #     timebudget_per_libary[lib][r] = f"{deep_fuzzing_time}s"
            # else:
            #     timebudget_per_libary[lib][r] = f"{int(deep_fuzzing_time/len(drivers_for_deep))}s"

    if simulate in ["full", "short"]:
        print("[INFO] Only simulation, here the drivers I would select:")
        for lib, drvs in drivers_to_keep.items():
            for r in range(1, n_runs+1):
                print(f"{lib} run {r}: {len(drvs)}")
                if simulate == "full":
                    for driver in drvs[r]:
                        d_path = f"workdir_X_X/{lib}/iter_{r}/drivers/{driver}"
                        print(f"{d_path}")

                    print("-" * 30)

        exit(0)
        
    # os.system("mkdir -p workdir_backup")
    # os.system("mv workdir_*_*/ workdir_backup")

    # from IPython import embed; embed(); exit(1)

    for lib, all_drvs in drivers_to_keep.items():
        for r in range(1, n_runs+1):
            drvs = all_drvs[r]
            print(f"{lib} {r}: {len(drvs)} drivers")
            for driver in drvs:

                # # cp compiled driver
                # os.system(f"mkdir -p workdir_X_X/{lib}/iter_{r}/drivers")
                # os.system(f"cp {rootdir}/workdir_X_X/{lib}/iter_{r}/drivers/{driver} workdir_X_X/{lib}/iter_{r}/drivers")

                # # cp source code driver
                # os.system(f"cp {rootdir}/workdir_X_X/{lib}/iter_{r}/drivers/{driver}.cc workdir_X_X/{lib}/iter_{r}/drivers")

                # cp profile driver
                # os.system(f"mkdir -p workdir_X_X/{lib}/iter_{r}/profiles")
                src = f"./{rootdir}/workdir_X_X/{lib}/iter_{r}/profiles/{driver}_profile"
                dst = f"./workdir_X_X/{lib}/iter_{r}/profiles"
                rel_path = os.path.join(*[".."] * dst.count(os.path.sep))
                os.system(f"ln -sf {rel_path}/{src} {dst}")

                # # cp cluster driver
                # os.system(f"mkdir -p workdir_X_X/{lib}/iter_{r}/cluster_drivers")
                # os.system(f"cp {rootdir}/workdir_X_X/{lib}/iter_{r}/cluster_drivers/{driver}_cluster workdir_X_X/{lib}/iter_{r}/cluster_drivers")

                # # cp corpus for driver
                # os.system(f"mkdir -p workdir_X_X/{lib}/iter_{r}/corpus")
                
                # if keepcorpus:
                #     os.system(f"cp -r {rootdir}/workdir_X_X/{lib}/iter_{r}/corpus_new/{driver} workdir_X_X/{lib}/iter_{r}/corpus")
                # else:
                #     os.system(f"cp -r {rootdir}/workdir_X_X/{lib}/iter_{r}/corpus/{driver} workdir_X_X/{lib}/iter_{r}/corpus")

                # cp metadata for driver
                # os.system(f"mkdir -p workdir_X_X/{lib}/iter_{r}/metadata")
                # os.system(f"cp -r {rootdir}/workdir_X_X/{lib}/iter_{r}/metadata/{driver}.meta workdir_X_X/{lib}/iter_{r}/metadata")
                # os.system(f"ln -fsr ")
                src = f"{rootdir}/workdir_X_X/{lib}/iter_{r}/metadata/{driver}.meta"
                dst = f"workdir_X_X/{lib}/iter_{r}/metadata/{driver}.meta"
                rel_path = os.path.join(*[".."] * dst.count(os.path.sep))
                os.system(f"ln -sf {rel_path}/{src} {dst}")
                
                # os.system(f"mkdir -p workdir_X_X/{lib}/iter_{r}/coverage_data")
                # os.system(f"cp -r {rootdir}/workdir_X_X/{lib}/iter_{r}/coverage_data/{driver}.profdata workdir_X_X/{lib}/iter_{r}/coverage_data")
                src = f"{rootdir}/workdir_X_X/{lib}/iter_{r}/coverage_data/{driver}.profdata"
                dst = f"workdir_X_X/{lib}/iter_{r}/coverage_data/{driver}.profdata"
                rel_path = os.path.join(*[".."] * dst.count(os.path.sep))
                os.system(f"ln -sf {rel_path}/{src} {dst}")

                # os.system(f"mkdir -p workdir_X_X/{lib}/iter_{r}/corpus_new")
                # os.system(f"cp -r workdir_X_X/{lib}/iter_{r}/corpus_new/{driver} workdir_X_X/{lib}/iter_{r}/corpus_new")

                # os.system(f"mkdir -p workdir_X_X/{lib}/iter_{r}/crashes/{driver}")


if __name__ == "__main__":
    _main()
