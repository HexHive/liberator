#!/usr/bin/env python3

import argparse

import score as scr

def _main():

    parser = argparse.ArgumentParser(description='Select stable drivers')
    parser.add_argument('-report', '-r', type=str, help='Report File', required=True)
    parser.add_argument('-rootdir', '-d', type=str, help='Driver Folder', required=False)

    args = parser.parse_args()

    report = args.report
    rootdir = args.rootdir

    libraries = scr.load_report(report, rootdir)
    
    best_drivers = {}

    # print(libraries)
    for lib, drvs in libraries.items():
        best_drvs = scr.get_best_drivers(drvs)

        best_drivers[lib] = best_drvs

    # FROM HERE    
    for lib, drvs in best_drivers.items():
        print(f"{lib}")
        for d in drvs:
            print(d)
        

if __name__ == "__main__":
    _main()