#!/usr/bin/python3

import argparse, csv

PROJECT_FOLDER="/workspaces/libfuzz"

import sys, os
sys.path.append(PROJECT_FOLDER)
from framework import * 
from generator import Configuration
from constraints import ConditionManager
import copy, json

# def get_utopia_data(utopia_folder):

#     ..

#     for f, p_b in uar["Array"].items():
#         f_clean = f.split("(")[0]
#         # print(f_clean)
#         if f_clean in api_strings and "[" not in f and p_b != -1:
#             # print(f"{f_clean} is found!!")

#             x1 = f.find("(")
#             x2 = f.find(")")
#             p_a = f[x1+1:x2]
            
#             real_utipia_api[f_clean] = (int(p_a), p_b)


NONE = "-"

def get_targets_data(targets):

    targets_data = {}    

    for t in os.listdir(targets):
        ft = os.path.join(targets, t)
        config_path = os.path.join(targets, t, "generator.toml")
        if os.path.isdir(ft) and os.path.isfile(config_path):
            try:
                config = Configuration(config_path)
                config.build_data_layout()
                config.build_condition_manager()

                targets_data[t] = copy.deepcopy(ConditionManager.instance())
            except:
                pass

        # if t == "libaom":
        #     apis = config.api_list_all
        #     for a in apis:
        #         cc = config.function_conditions.get_function_conditions(a.function_name)
        #         for arg in cc.argument_at:
        #             if arg.len_depends_on != "":
        #                 print(a)
            
            # print("get_targets_data")
            # from IPython import embed; embed(); exit(1)

    return targets_data
            
def parse_gt(groundtruth):

    gt = {}
    
    with open(groundtruth) as f:
        gt_csv = csv.DictReader(f, delimiter=',', quotechar='"')
        for l in gt_csv:
            library = l["Library"]
            function, pos  = l["API function:argument (-1 return)"].split(":")

            arg_info = {}
            arg_info["malloc_size"] = l["malloc size"] == "TRUE"
            arg_info["file_path"] = l["file path"] == "TRUE"
            arg_info["buffer"] = l["buffer (var len)"] == "TRUE"
            arg_info["length"] = l["length (var len)"]
            arg_info["create"] = l["create"] == "TRUE"
            arg_info["static"] = l["static"] == "TRUE"
            arg_info["source"] = l["source"] == "TRUE"
            arg_info["sink"] = l["sink"] == "TRUE"
            arg_info["init"] = l["init api"] == "TRUE"

            l_info = gt.get(library, {})
            f_info = l_info.get(function, {})
            f_info[pos] = arg_info
            l_info[function] = f_info
            gt[library] = l_info

    return gt


def get_tot(s, key):

    x = 0
    for k, v in s.items():
        if k.startswith(key):
            x += v

    return x

def get_details(s, key):
    tp = 0
    fp = 0
    tn = 0
    fn = 0
    for k, v in s.items():
        if k.startswith(key):
            if k.endswith("_tp"):
                tp = v
            if k.endswith("_fp"):
                fp = v
            if k.endswith("_tn"):
                tn = v
            if k.endswith("_fn"):
                fn = v

    return tp, fp, tn, fn

def get_accuracy(s, key):
    tot = get_tot(s, key)
    tp, _, tn, _ = get_details(s, key)

    if tot == 0:
        return NONE
            
    return f"{((tp + tn) / tot):0.1%}"
    
    
def get_precision(s, key):
    # tot = get_tot(s, key)
    tp, fp, _, _ = get_details(s, key)

    if tp + fp == 0:
        return NONE

    return f"{(tp / (tp + fp)):0.2%}"

def _main():
    parser = argparse.ArgumentParser(description='Counts the API used')
    parser.add_argument('-groundtruth', '-g', type=str, help='Ground Trurth CSV File (ask the authors)', required=True)
    parser.add_argument('-targets', '-t', type=str, help='Folder with target libraries', required=True)
    # parser.add_argument('-utopia', '-u', type=str, help='Folder with Utopia resultstarget', required=True)

    args = parser.parse_args()

    groundtruth = args.groundtruth
    targets = args.targets
    # utopia = args.utopia
    
    gt_data = parse_gt(groundtruth)
    targets_data = get_targets_data(targets)

    stats = {}
    # source_tp = 0
    # source_fp = 0
    # source_tn = 0
    # source_fn = 0
    
    for t, cond in targets_data.items():
        print(f"doing {t}")
        fp_l = set()
        fn_l = set()
        stats[t] = {"source_tp": 0, "source_fp": 0, "source_tn": 0, "source_fn": 0, "init_tp": 0, "init_fp": 0, "init_tn": 0, "init_fn": 0, "sink_tp": 0, "sink_fp": 0, "sink_tn": 0, "sink_fn": 0, "varlen_tp": 0, "varlen_fp": 0, "malloc_tp": 0, "malloc_fp": 0, "malloc_tn": 0, "malloc_fn": 0, "file_path_tp": 0, "file_path_fp": 0, "file_path_tn": 0, "file_path_fn": 0, "create_tp": 0, "create_fp": 0, "create_tn": 0, "create_fn": 0}
        for a in cond.api_list_all:
            a_gt = gt_data[t][a.function_name]
            # print("xx")
            # from IPython import embed; embed(); exit(1)
            if a in cond.get_source_api():
                if a_gt["-1"]["source"]:
                    # source_tp += 1
                    stats[t]["source_tp"] += 1
                else:
                    # source_fp += 1
                    stats[t]["source_fp"] += 1
                    fp_l.add(a)
            else:
                if a_gt["-1"]["source"]:
                    # source_fn += 1
                    stats[t]["source_fn"] += 1
                    fn_l.add(a)
                else:
                    # source_tn += 1
                    stats[t]["source_tn"] += 1

            if a in cond.get_init_api():
                if a_gt["-1"]["init"]:
                    # source_tp += 1
                    stats[t]["init_tp"] += 1
                else:
                    # source_fp += 1
                    stats[t]["init_fp"] += 1
            else:
                if a_gt["-1"]["init"]:
                    # source_fn += 1
                    stats[t]["init_fn"] += 1
                    fn_l.add(a)
                else:
                    # source_tn += 1
                    stats[t]["init_tn"] += 1

            if a in cond.get_sink_api():
                if a_gt["-1"]["sink"]:
                    # source_tp += 1
                    stats[t]["sink_tp"] += 1
                else:
                    # source_fp += 1
                    stats[t]["sink_fp"] += 1
                    fp_l.add(a)
            else:
                if a_gt["-1"]["sink"]:
                    # source_fn += 1
                    stats[t]["sink_fn"] += 1
                else:
                    # source_tn += 1
                    stats[t]["sink_tn"] += 1

            a_cond = cond.conditions.get_function_conditions(a.function_name)
            # "varlen_tp": 0, "varlen_fp": 0, "varlen_tn": 0, "varlen_fn": 0
            for n, arg in enumerate(a_cond.argument_at):
                if arg.len_depends_on == a_gt[f"{n}"]["length"]:
                    stats[t]["varlen_tp"] += 1
                else:
                    stats[t]["varlen_fp"] += 1

                # print("xxxaaa")
                # from IPython import embed; embed(); exit(1)
                if arg.is_malloc_size:
                    if a_gt[f"{n}"]["malloc_size"]:
                        stats[t]["malloc_tp"] += 1
                    else:
                        stats[t]["malloc_fp"] += 1
                else:
                    if a_gt[f"{n}"]["malloc_size"]:
                        stats[t]["malloc_fn"] += 1
                    else:
                        stats[t]["malloc_tn"] += 1

                
                if arg.is_file_path:
                    if a_gt[f"{n}"]["file_path"]:
                        stats[t]["file_path_tp"] += 1
                    else:
                        stats[t]["file_path_fp"] += 1
                        fp_l.add(a)
                else:
                    if a_gt[f"{n}"]["file_path"]:
                        stats[t]["file_path_fn"] += 1
                        fn_l.add(a)
                    else:
                        stats[t]["file_path_tn"] += 1



                # "": 0, "": 0, "malloc_tp": 0, "malloc_fp": 0

        # if t == "pthreadpool":
        #     from IPython import embed; embed(); exit(1)
        print(f"done: {t}")

    # with open("rq1_libfuzz.json", "w") as f:
    #     json.dump(stats, f)
    # # from IPython import embed; embed(); exit(1)

    print("library;source;init;sink;var-len;malloc;file-path")
    for l, s in sorted(stats.items()):
        
        acc = get_accuracy(s, "source")
        # prec = get_precision(s, "source")
        source = f"{acc}"

        acc = get_accuracy(s, "sink")
        # prec = get_precision(s, "sink")
        # sink = f"{acc}/{prec}"
        sink = f"{acc}"
        
        # if s["init_tp"] + s["init_fn"] == 0:
        #     init = NONE
        # else:
        #     init = s["init_tp"] / (s["init_tp"] + s["init_fn"])
        acc = get_accuracy(s, "init")
        init = f"{acc}"

        acc = get_accuracy(s, "varlen")
        varlen = f"{acc}"
        # if s["varlen_tp"] + s["varlen_fp"] == 0:
        #     varlen = NONE
        # else:
        #     varlen = s["varlen_tp"] / (s["varlen_tp"] + s["varlen_fp"])
        #     varlen = f"{varlen:0.2%}"

        acc = get_accuracy(s, "file_path")
        filepath = f"{acc}"

        # if s["malloc_tp"] + s["malloc_fn"] == 0:
        #     malloc = NONE
        # else:
        #     malloc = s["malloc_tp"] / (s["malloc_tp"] + s["malloc_fn"])
        #     malloc = f"{malloc:0.2%}"

        acc = get_accuracy(s, "malloc")
        malloc = f"{acc}"
        
        print(f"{l};{source};{sink};{init};{varlen};{filepath};{malloc}")
        
    

if __name__ == "__main__":
    _main()