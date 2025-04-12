#! /usr/bin/python3

import sys
import os
import argparse
import re
from pprint import pprint




def parse_file(file_path):
    with open(file_path, "r") as file:
        apis = set()
        for line in file:
            # regex to find api name: "call .*: API  ?"
            regex = r" call .*: (.*) \?"
            res = re.findall(regex, line)
            if len(res)> 0:
                for r in res:
                    apis.add(r)
        
        return apis


def parse_library(library_folder_path, ground_truth):
    iterarions = 5

    api_sets = []
    for i in range(1, iterarions + 1):
        iteration = os.path.join(library_folder_path, "output" if i == 1 else "output_" + str(i), "queue")
        api_sets.append(set())
        # if file does not exist, return
        if not os.path.exists(iteration):
            continue

        # list the file in the `iteration folder`/queue
        files = os.listdir(iteration)
        for file in files:
            apis = parse_file(file_path=os.path.join(iteration, file))
            api_sets[i-1].update(apis)
        
        # opens ground truth csv called total_apis.csv
        to_remove = []
        for api in api_sets[i-1]:
            if api not in ground_truth:
                to_remove.append(api)
        for api in to_remove:
            api_sets[i-1].remove(api)
            
    return api_sets 


def dump_coverage(libraries):
    res = {}
    for lib in libraries.keys():
        lens = []
        for i in range(0, len(libraries[lib])):
            lens.append(len(libraries[lib][i]))
            if(lib == "libpcap"):
                pprint(libraries[lib][i])
        if(sum(lens) == 0):
            continue
        print(lens)
        res[lib] =  sum(lens) / len(lens)
    return res

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--folder", help="Specify the folder", required=True)
    args = parser.parse_args()
    # find the different targets in the folder
    targets = os.listdir(args.folder)
    coverage = {}
    ground_truth = {}
    with open(os.path.join(args.folder, "total_apis.csv"), "r") as file:
        for fullline in file:
            line = fullline.split(",")
            if line[0] not in ground_truth.keys():
                ground_truth[line[0]] = set()
            ground_truth[line[0]].add(line[1].replace("\n", ""))


    for target in targets:
        if not os.path.isdir(os.path.join(args.folder, target)) or target not in ground_truth.keys():
            continue
        print("Target: ", target)
        coverage[target] = parse_library(library_folder_path=os.path.join(args.folder, target), ground_truth=ground_truth[target])
    res = dump_coverage(coverage)
    for lib in ground_truth.keys():
        print(lib, ":", len(ground_truth[lib]))
    pprint(res)



if __name__ == "__main__":
    main()
