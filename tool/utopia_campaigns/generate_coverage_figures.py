#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
from os import listdir
import argparse

def get_function_coverages(coverage_file):
    result = {}

    with open(coverage_file) as fcoverage:
        for line in fcoverage:
            line = line.strip()
            if not line:
                continue
            if line.startswith("-"):
                continue
            if line.startswith("Name"):
                continue
            if line.startswith("File "):
                continue
            line = line.split()
            function_name = line[0]
            coverage = float(line[3].rstrip("%"))
            result[function_name] = coverage
    return result

def get_coverage_files_for_drivers(project, list_of_drivers):
    result = {}
    for ndrivers, napis, driver_name in list_of_drivers:
        result[f"{ndrivers}_{napis}_{driver_name}"] = f"./workdir_{ndrivers}_{napis}/{project}/coverage_data/{driver_name}/functions"
    return result

def get_coverage_files_for_project(project):
    result = {}
    drivers = listdir(f"./exp/{project}/output/fuzzers")

    for driver in drivers:
        result[driver] = f"./coverage_data/{project}/{driver}/functions"
    result["total"] = f"./coverage_data/{project}/functions"
    return result


def get_coverage_datas_for_project(project):
    coverage_files = get_coverage_files_for_project(project)
    coverage_datas = {}
    function_hit_or_not = {}
    functions = []

    for name in sorted(coverage_files.keys()):
        coverage_file = coverage_files[name]
        coverages = get_function_coverages(coverage_file)

        functions.append(list(coverages.keys()))

    functions = list(set.intersection(*map(set, functions)))

    for name in sorted(coverage_files.keys()):
        coverage_file = coverage_files[name]
        coverages = get_function_coverages(coverage_file)

        coverage_list = []

        for function in functions:
            coverage_list.append(coverages[function])
            if coverages[function] > 0:
                function_hit_or_not[function] = 100
            else:
                if function not in function_hit_or_not:
                    function_hit_or_not[function] = 0
        coverage_datas[name] = np.array(coverage_list)

    hit_or_not = []
    for function in functions:
        hit_or_not.append(function_hit_or_not[function])
    coverage_datas["hit"] = np.array(hit_or_not)
    return coverage_datas

def draw_heatmap(project, coverage_datas):
    # print(coverage_datas["hit"])
    # return
    # Set up the figure and axes with a smaller figsize
    fig, axes_tuple = plt.subplots(nrows=len(coverage_datas), figsize=(50, 50))

    # Create a colormap
    cmap = plt.cm.Greys

    # Normalize coverage percentages to the range [0, 1]
    norm = plt.Normalize(0, 100)

    idx = 0
    names = [name for name in sorted(coverage_datas.keys()) if name not in ["total", "hit"]] + ["total", "hit"]
    for name in names:
        coverage_data = coverage_datas[name]
        normalized_coverage = norm(coverage_data)
        x = np.arange(len(coverage_data))
        bar_height = 1
        axes_tuple[idx].bar(x, height=bar_height, width=1, color=cmap(normalized_coverage), edgecolor='none', )
        axes_tuple[idx].xaxis.set_visible(False)
        # axes_tuple[idx].yaxis.set_visible(False)
        axes_tuple[idx].set_ylabel(name, fontsize=2, rotation=0)
        plt.setp(axes_tuple[idx].get_xticklabels(), visible=False)
        plt.setp(axes_tuple[idx].get_yticklabels(), visible=False)
        axes_tuple[idx].tick_params(axis='both', which='both', length=0)
        idx += 1


    axes_tuple[0].set_title(f"{project} Coverage Heatmap")
    plt.subplots_adjust(hspace=0)
    plt.savefig(f'{project}_heatmapp.png', dpi=300, bbox_inches='tight')
    # Display the plot
    plt.show()

def heatmap_for_library(project):
    coverage_datas = get_coverage_datas_for_project(project)
    draw_heatmap(project, coverage_datas)


# heatmap_for_library("pthreadpool")
# print("done pthreadpool")
# heatmap_for_library("cpu_features")
# print("done cpu_features")
heatmap_for_library("libvpx")
# print("done libvpx")
# heatmap_for_library("libhtp")
# print("done libhtp")
# heatmap_for_library("libaom")
# print("done libaom")
