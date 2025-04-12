#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
from os import listdir
import argparse


fuzzing_campaigns = "../../../fuzzing_campaigns"

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
    for ndrivers in [20]:
        for napis in [2, 4, 8, 16, 32]:
            try:
                project_folder = f"{fuzzing_campaigns}/workdir_{ndrivers}_{napis}/{project}"
                drivers = [driver[:-3] for driver in listdir(f"{project_folder}/drivers") if driver.endswith(".cc")]
                for driver_name in drivers:
                    result[f"{ndrivers}_{napis}_{driver_name}"] = f"{fuzzing_campaigns}/workdir_{ndrivers}_{napis}/{project}/coverage_data/{driver_name}/report"
                result["total"] = f"{fuzzing_campaigns}/total_library_coverage/{project}/report"
            except FileNotFoundError:
                continue
    return result


def get_coverage_datas_for_drivers(project):
    coverage_files = get_coverage_files_for_drivers(project)
    coverage_datas = {}
    functions = []


    for name in sorted(coverage_files.keys()):
        coverage_file = coverage_files[name]
        coverage = get_driver_coverage(coverage_file)

        coverage_datas[name] = coverage

    return coverage_datas


def draw_barchart(project, data_dict):
    x_values = []
    y_values = []


    for key, val in sorted(data_dict.items(), key=lambda x: x[1]):
        x_values.append(key)
        y_values.append(val)

    # Create a bar chart
    plt.figure(figsize=(10, 6))

    norm = plt.Normalize(0, 100)
    plt.bar(x_values, y_values, color=plt.cm.RdYlGn(norm(y_values)))


    # Add labels and title
    plt.xlabel("Driver")
    plt.ylabel("Coverage in %")
    plt.title(f"{project} driver coverage")
    plt.xticks(rotation=45)
    # plt.xticks(x_values, rotation=45)

    # plt.xticks(np.arange(min(x_values), max(x_values)+1, 1.0), fontsize=0)
    # plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)

    # Show the chart
    plt.tight_layout()
    plt.savefig(f'{project}_barchart.png', dpi=300, bbox_inches='tight')
    plt.show()


def barchart_for_library(project):
    coverage_datas = get_coverage_datas_for_drivers(project)
    draw_barchart(project, coverage_datas)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Produce barchart')
    parser.add_argument('--target', '-t', type=str, 
                        help='Target to analyse', required=True)
    args = parser.parse_args()
    target = args.target
    barchart_for_library(target)
