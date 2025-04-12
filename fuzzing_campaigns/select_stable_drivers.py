#!/usr/bin/env python3

import csv, argparse, math
import numpy as np
import os, sys

PROJECT_FOLDER="../"
sys.path.append(PROJECT_FOLDER)

import tool.misc.score as scr

seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}

def normalize_time_boudget(s):
    return int(s[:-1]) * seconds_per_unit[s[-1]]

def _main():

    parser = argparse.ArgumentParser(description='Select stable drivers')
    parser.add_argument('-report', '-r', type=str, 
                        help='Report File', required=True)
    parser.add_argument('-rootdir', '-d', type=str, 
                        help='Driver Folder', required=False)
    parser.add_argument('-threshold', '-t', type=float, default=0.10,
                        help='Threshold for selection', required=False)
    parser.add_argument('-simulate', '-s', choices=['full', 'short'], const='full', nargs='?',
                        help='Simulation only, not moving files around', 
                        required=False)
    parser.add_argument('-timebudget', '-b', type=str,
                        help='Compute budget time for long testing', 
                        required=True)
    parser.add_argument('-keepcorpus', '-k', action='store_true', help='Keep corpus from previous campaign')

    args = parser.parse_args()

    report = args.report
    rootdir = args.rootdir
    simulate = args.simulate
    threshold = args.threshold
    timebudget = normalize_time_boudget(args.timebudget)
    keepcorpus = args.keepcorpus
    
    libraries = scr.load_report(report, rootdir)

    best_drivers = {}

    timebudget_per_libary = {}

    # print(libraries)
    for lib, drvs in libraries.items():
        best_drvs = scr.get_best_drivers(drvs, threshold)
        best_drivers[lib] = best_drvs
        timebudget_per_libary[lib] = f"{int(timebudget/len(best_drvs))}s"
        # print("-" * 10)
        # print(lib)
        # print(best_drvs)

    if simulate in ["full", "short"]:
        print("[INFO] Only simulation, here the drivers I would select:")
        for lib, drvs in best_drivers.items():
            tb = timebudget_per_libary[lib]
            print(f"{lib}: {len(drvs)} drivers w/ timebudget {tb}")
            if simulate == "full":
                for d in drvs:
                    n_drivers = d['n_drivers']
                    n_apis = d['n_apis']
                    driver = d['driver']
                    cov = d['cov']

                    d_path = f"workdir_{n_drivers}_{n_apis}/{lib}/drivers/{driver}"
                    print(f"{d_path}: {cov}")

                print("-" * 30)

        exit(0)
        
    os.system("mkdir -p workdir_backup")
    os.system("mv workdir_*_*/ workdir_backup")

    # from IPython import embed; embed(); exit(1)

    for lib, drvs in best_drivers.items():
        print(f"{lib}: {len(drvs)} drivers")
        for d in drvs:
            n_drivers = d['n_drivers']
            n_apis = d['n_apis']
            driver = d['driver']

            # cp compiled driver
            os.system(f"mkdir -p workdir_{n_drivers}_{n_apis}/{lib}/drivers")
            os.system(f"cp {rootdir}/workdir_{n_drivers}_{n_apis}/{lib}/drivers/{driver} workdir_{n_drivers}_{n_apis}/{lib}/drivers")

            # cp source code driver
            os.system(f"cp {rootdir}/workdir_{n_drivers}_{n_apis}/{lib}/drivers/{driver}.cc workdir_{n_drivers}_{n_apis}/{lib}/drivers")

            # cp profile driver
            os.system(f"mkdir -p workdir_{n_drivers}_{n_apis}/{lib}/profiles")
            os.system(f"cp {rootdir}/workdir_{n_drivers}_{n_apis}/{lib}/profiles/{driver}_profile workdir_{n_drivers}_{n_apis}/{lib}/profiles")

            # cp cluster driver
            os.system(f"mkdir -p workdir_{n_drivers}_{n_apis}/{lib}/cluster_drivers")
            os.system(f"cp {rootdir}/workdir_{n_drivers}_{n_apis}/{lib}/cluster_drivers/{driver}_cluster workdir_{n_drivers}_{n_apis}/{lib}/cluster_drivers")

            # cp corpus for driver
            os.system(f"mkdir -p workdir_{n_drivers}_{n_apis}/{lib}/corpus")
            
            if keepcorpus:
                os.system(f"cp -r {rootdir}/workdir_{n_drivers}_{n_apis}/{lib}/results/iter_1/corpus_new/{driver} workdir_{n_drivers}_{n_apis}/{lib}/corpus")
            else:
                os.system(f"cp -r {rootdir}/workdir_{n_drivers}_{n_apis}/{lib}/corpus/{driver} workdir_{n_drivers}_{n_apis}/{lib}/corpus")

            # cp metadata for driver
            os.system(f"mkdir -p workdir_{n_drivers}_{n_apis}/{lib}/metadata")
            os.system(f"cp -r {rootdir}/workdir_{n_drivers}_{n_apis}/{lib}/metadata/{driver}.meta workdir_{n_drivers}_{n_apis}/{lib}/metadata")

            # os.system(f"mkdir -p workdir_{n_drivers}_{n_apis}/{lib}/corpus_new")
            # os.system(f"cp -r workdir_{n_drivers}_{n_apis}/{lib}/corpus_new/{driver} workdir_{n_drivers}_{n_apis}/{lib}/corpus_new")

            os.system(f"mkdir -p workdir_{n_drivers}_{n_apis}/{lib}/crashes/{driver}")

    # save timebudget per library
    with open("./time_budget.csv", "w") as f:
        for l, t in timebudget_per_libary.items():
            f.write(f"{l}|{t}\n")


if __name__ == "__main__":
    _main()
