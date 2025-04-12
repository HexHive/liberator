#!/usr/bin/env python3

import argparse
import numpy as np
import score as scr
from tabulate import tabulate
import matplotlib.pyplot as plt

def print_summary(libraries):
    for lib, drvs in dict(sorted(libraries.items())).items():
        max_cov = 0
        n_drv_cov = 0
        n_drv_cov_1 = 0
        n_crashes_w_cov = []
        n_unicrsh_w_cov = []
        for d in drvs:
            if d["cov"] > 0:
                n_drv_cov += 1
                n_crashes_w_cov += [d["n_crashes"]]
                n_unicrsh_w_cov += [d["n_unicrsh"]]
            if d["cov"] > max_cov:
                max_cov = d["cov"]
            if d["cov"] >= 0.01:
                n_drv_cov_1 += 1
        
        tot_drv = len(drvs)
        n_drv_cov_perc = float(n_drv_cov)/tot_drv*100
        n_drv_cov_1_perc = float(n_drv_cov_1)/tot_drv*100
        max_cov = max_cov*100
        avg_crashes_w_cov = np.average(n_crashes_w_cov)
        std_crashes_w_cov = np.std(n_crashes_w_cov)
        avg_unicrsh_w_cov = np.average(n_unicrsh_w_cov)
        std_unicrsh_w_cov = np.std(n_unicrsh_w_cov)

        print(f"{lib}:")
        print(f"\tcov >  0%: {n_drv_cov}/{tot_drv} {n_drv_cov_perc:.2f}%")
        print(f"\tcov > 10%: {n_drv_cov_1}/{tot_drv} {n_drv_cov_1_perc:.2f}%")
        print(f"\tmax cov: {max_cov:.2f}%")
        print(f"\t#crashes (cov != 0): avg {avg_crashes_w_cov:.2f} std {std_crashes_w_cov:.2f}")
        print(f"\t#unique crashes (cov != 0): avg {avg_unicrsh_w_cov:.2f} std {std_unicrsh_w_cov:.2f}")

def print_table(libraries):

    rows = {}

    all_cols = []

    for lib, drv in libraries.items():
        api_score_raw = {}

        for d in drv:
            n_api = d["n_apis"]
            score = d["score"]

            all_scores = api_score_raw.get(n_api, [])
            all_scores += [score]
            api_score_raw[n_api] = all_scores

        # print(lib)
        # print(api_score)
        # exit(1)
        rows[lib] = {}
        for n_api, raw in api_score_raw.items():
            rows[lib][n_api] = np.median(raw)
            # rows[lib][n_api] = np.average(raw)
            # s = len(raw)
            # print(f"{lib} {n_api} = {s}")

    
    all_n_api = set()
    for lib, score in rows.items():
        # print(lib)
        # print(score)
        # print("----")
        all_n_api = all_n_api.union(set([int(s) for s in score.keys()]))

    all_cols = sorted(list(all_n_api))
    
    table = []
    table += [["library"] + all_cols + ["best conf."]]
    for lib, score in rows.items():
        orered_val = sorted(score.items(), key=lambda x: int(x[0]))
        rank_score = sorted(score.items(), key=lambda x: float(x[1]))
        best_conf_1 = int(rank_score[-1][0])
        best_conf_2 = int(rank_score[-2][0])
        table += [[lib] + [o[1] for o in orered_val] + 
                  [f"{best_conf_1} - {best_conf_2}"]]

    print(tabulate(table, headers='firstrow'))

def print_distribution(libraries):

    for lib, drv in libraries.items():
        covs = []

        for d in drv:
            # n_api = d["n_apis"]
            cov = d["cov"]
            covs += [cov]
  
        plt.clf()
        plt.hist(covs, edgecolor="red", bins=50) 

        # print(dist)
        # plt.hist(dist)
        plt.savefig(f"{lib}.png")
        # print(lib)
        # exit()



def _main():
    parser = argparse.ArgumentParser(description='Select stable drivers')
    parser.add_argument('-report', '-r', type=str, help='Report File', required=True)
    parser.add_argument('-rootdir', '-d', type=str, help='Driver Folder', required=False)

    args = parser.parse_args()
    
    report = args.report
    rootdir = args.rootdir

    libraries = scr.load_report(report, rootdir)

    print_summary(libraries)
    # print_table(libraries)
    # print_distribution(libraries)

if __name__ == "__main__":
    _main()