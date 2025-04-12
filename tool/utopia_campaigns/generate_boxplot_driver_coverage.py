#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
from os import listdir
import argparse


def get_driver_coverage(coverage_file):
    region_cover = 0
    with open(coverage_file) as report:
        for line in report:
            line = line.strip()
            if not line:
                continue
            if not line.startswith("TOTAL"):
                continue
            line = line.split()
            region_cover = float(line[12].rstrip("%"))
    return region_cover

def get_coverage_files_for_drivers(project):
    result = {}
    drivers = listdir(f"./exp/{project}/output/fuzzers")

    for driver in drivers:
        result[driver] = f"./coverage_data/{project}/{driver}/report"

    result["total"] = f"./coverage_data/{project}/report"
    return result

def get_coverage_datas_for_project(project):
    coverage_files = get_coverage_files_for_drivers(project)
    coverage_datas = {}


    for name in sorted(coverage_files.keys()):
        coverage_file = coverage_files[name]
        coverage = get_driver_coverage(coverage_file)
        coverage_datas[name] = coverage

    return coverage_datas

def draw_barchart(project, data_dict):
    x_values = []
    y_values = []


    # for key, val in sorted(data_dict.items(), key=lambda x: x[1]):
    #     x_values.append(key)
    #     y_values.append(val)

    for idx, val in enumerate(sorted(data_dict.values())):
        x_values.append(idx)
        y_values.append(val)

    # Create a bar chart
    plt.figure(figsize=(10, 6))

    norm = plt.Normalize(0, 100)
    plt.bar(x_values, y_values, color=plt.cm.RdYlGn(norm(y_values)))


    # Add labels and title
    plt.xlabel("Driver")
    plt.ylabel("Coverage in %")
    plt.title(f"{project} driver coverage")
    # plt.xticks(rotation=45)
    # plt.xticks(x_values, rotation=45)

    plt.xticks(np.arange(min(x_values), max(x_values)+1, 1.0), fontsize=0)
    # plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)

    # Show the chart
    plt.tight_layout()
    plt.savefig(f'{project}_barchart.png', dpi=300, bbox_inches='tight')
    plt.show()


def barchart_for_library(project):
    coverage_datas = get_coverage_datas_for_project(project)
    draw_barchart(project, coverage_datas)


barchart_for_library("cpu_features")
barchart_for_library("libaom")
barchart_for_library("libhtp")
barchart_for_library("libvpx")
barchart_for_library("minijail")
barchart_for_library("pthreadpool")

