#!/usr/bin/env python3

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from os import listdir
import argparse


fuzzing_campaigns = "../../../fuzzing_campaigns"

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
            coverage = float(line[9].rstrip("%"))
            result[function_name] = coverage
    return result

def get_coverage_files_for_drivers(project, list_of_drivers=[]):
    result = {}
    if list_of_drivers:
        for ndrivers, napis, driver_name in list_of_drivers:
            result[f"{ndrivers}_{napis}_{driver_name}"] = f"{fuzzing_campaigns}/workdir_{ndrivers}_{napis}/{project}/coverage_data/{driver_name}/functions"
        return result
    for ndrivers in [20]:
        for napis in [2, 4, 8, 16, 32]:
            try:
                project_folder = f"{fuzzing_campaigns}/workdir_{ndrivers}_{napis}/{project}"
                drivers = [driver[:-3] for driver in listdir(f"{project_folder}/drivers") if driver.endswith(".cc")]
                for driver_name in drivers:
                    result[f"{ndrivers}_{napis}_{driver_name}"] = f"{fuzzing_campaigns}/workdir_{ndrivers}_{napis}/{project}/coverage_data/{driver_name}/functions"
                result["total"] = f"{fuzzing_campaigns}/total_library_coverage/{project}/functions"
            except FileNotFoundError:
                continue
    return result

def get_coverage_files_for_configuration(project, napis, ndrivers):
    result = {}
    project_folder = f"{fuzzing_campaigns}/workdir_{napis}_{ndrivers}/{project}"
    drivers = [driver[:-3] for driver in listdir(f"{project_folder}/drivers") if driver.endswith(".cc")]

    for driver in drivers:
        result[driver] = f"{project_folder}/coverage_data/{driver}/functions"
    result["total"] = f"{project_folder}/coverage_data/total/functions"
    return result

def get_coverage_datas_for_drivers(project, list_of_drivers=[]):
    coverage_files = get_coverage_files_for_drivers(project, list_of_drivers)
    coverage_datas = {}
    function_hit_or_not = {}
    functions = []

    for name in sorted(coverage_files.keys()):
        coverage_file = coverage_files[name]
        coverages = get_function_coverages(coverage_file)

        functions.append(list(coverages.keys()))

    functions = sorted(list(set.intersection(*map(set, functions))))

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
        coverage_datas[name] = coverage_list
    hit_or_not = []

    for function in functions:
        hit_or_not.append(function_hit_or_not[function])
    coverage_datas["hit"] = hit_or_not

    return coverage_datas

def get_coverage_datas_for_configuration(project, ndrivers, napis):
    coverage_files = get_coverage_files_for_configuration(project, ndrivers, napis)
    coverage_datas = {}
    function_hit_or_not = {}
    functions = []

    for name in sorted(coverage_files.keys()):
        coverage_file = coverage_files[name]
        coverages = get_function_coverages(coverage_file)

        functions.append(list(coverages.keys()))

    functions = sorted(list(set.intersection(*map(set, functions))))

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


def draw_figure_1(project, coverage_datas):
    # Set up the figure and axes with a smaller figsize
    fig, axes_tuple = plt.subplots(nrows=len(coverage_datas), figsize=(20, 20))

    # Create a colormap
    cmap = plt.cm.RdYlGn

    # Normalize coverage percentages to the range [0, 1]
    norm = plt.Normalize(0, 100)
    idx = 0

    names = [name for name in sorted(coverage_datas.keys()) if name not in ["total", "hit"]] +  ["total", "hit"]

    for name in names:
        coverage_data = coverage_datas[name]
        normalized_coverage = norm(coverage_data)
        x = np.arange(len(coverage_data))
        bar_height = 1
        axes_tuple[idx].bar(x, height=bar_height, width=1, color=cmap(normalized_coverage), edgecolor='none', )
        axes_tuple[idx].xaxis.set_visible(False)
        axes_tuple[idx].set_ylabel(name, fontsize=2, rotation=40)
        axes_tuple[idx].axis('off')
        plt.setp(axes_tuple[idx].get_xticklabels(), visible=False)
        plt.setp(axes_tuple[idx].get_yticklabels(), visible=False)
        axes_tuple[idx].tick_params(axis='both', which='both', length=0)
        idx += 1

    axes_tuple[0].set_title(f"{project} Coverage Heatmap")
    plt.subplots_adjust(hspace=0)
    plt.savefig(f'{project}_heatmap_v1.png', dpi=300, bbox_inches='tight')
    # Display the plot
    plt.show()

def draw_figure_2(project, coverage_data):
    data = []
    names = [name for name in sorted(coverage_data.keys()) if name not in ["total", "hit"]] +  ["total", "hit"]
    for name in names:
        data.append(coverage_data[name])
    data = np.array(data)

    # fig, ax = plt.subplots()
    # im = ax.imshow(data)

    # # Show all ticks and label them with the respective list entries
    # # ax.set_xticks(np.arange(len(farmers)), labels=names)
    # ax.set_yticks(np.arange(len(names)), labels=names)

    # # Rotate the tick labels and set their alignment.
    # # plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
    #         # rotation_mode="anchor")

    # # Loop over data dimensions and create text annotations.
    # for i in range(len(names)):
    #     for j in range(len(coverage_data[name])):
    #         text = ax.text(j, i, data[i, j],
    #                     ha="center", va="center", color="w")

    # ax.set_title("Harvest of local farmers (in tons/year)")
    # fig.tight_layout()
    # plt.savefig(f'{project}_heatmap_v2.png')


    fig, ax = plt.subplots(figsize=(100, 50))
    sns.heatmap(data, cmap=plt.cm.Greys, xticklabels=False, yticklabels=False, cbar=False, linewidths=0.00001)
    plt.savefig(f'{project}_heatmap.png')
    plt.show()


def heatmap_for_library_configuration(project, ndrivers, napis):
    coverage_datas = get_coverage_datas_for_configuration(
        project, ndrivers, napis)
    draw_figure_2(project, coverage_datas)


def heatmap_for_library_drivers(project, list_of_drivers):
    coverage_datas = get_coverage_datas_for_drivers(project, list_of_drivers)
    draw_figure_2(project, coverage_datas)


def heatmap_for_library_all_drivers(project):
    coverage_datas = get_coverage_datas_for_drivers(project)
    draw_figure_2(project, coverage_datas)



if __name__ == "__main__":
    

    parser = argparse.ArgumentParser(description='Produce heat-map')
    parser.add_argument('--target', '-t', type=str, 
                        help='Target to analyse', required=True)
    subparsers = parser.add_subparsers(help='sub-command help', 
            dest="mode")
    

    # create the parser for the "a" command

    parser_a = subparsers.add_parser('configuration', 
            help='Heat map per library and configuration')
    parser_a.add_argument('--ndriver', type=int, help='N. Drivers')
    parser_a.add_argument('--napis', type=int, help='N. APIs')

    # create the parser for the "b" command

    parser_b = subparsers.add_parser('custom',
            help='Heat map with custom drivers')
    parser_b.add_argument('--inputfile', type=str, help='Input file')

    parser_b = subparsers.add_parser('library',
            help='Heat map with custom drivers')

    args = parser.parse_args()

    # print(args)

    target = args.target

    if args.mode == "configuration":
        napis = args.napis
        ndrivers = args.ndrivers
        heatmap_for_library_configuration(target, ndrivers, napis)
    elif args.mode == "custom":
        driver_list = get_driver_list(args.inputfile)
        heatmap_for_library_drivers(target, driver_list)
    else:
        heatmap_for_library_all_drivers(target)
    