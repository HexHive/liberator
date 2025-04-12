#!/usr/bin/env python3

PROJECT_FOLDER="/workspaces/libfuzz"

import sys, os
sys.path.append(PROJECT_FOLDER)

import argparse
from framework import * 
from generator import Configuration
from constraints import ConditionManager
import logging
import json


def __main():
    
    parser = argparse.ArgumentParser(description='Get all APIs for each library')
    parser.add_argument('--targets', '-t', type=str, help='Targets folder', required=True)
    parser.add_argument('--utopia', '-u', type=str, help='Folders that contain Utopia analysis results', required=True)

    args = parser.parse_args()

    targets = args.targets
    utopia_anal_result = args.utopia

    # libs = set()

    # api_per_lib = set()

    # for t in os.listdir(targets):

    api_strings = set()

    t = "libaom"
    ft = os.path.join(targets, t)
    config_path = os.path.join(targets, t, "generator.toml")
    if os.path.isdir(ft) and os.path.isfile(config_path):
        try:
            config = Configuration(config_path)
            config.build_data_layout()
            config.build_condition_manager()
            api_list_all = config.api_list_all
            # api_per_lib.add((t, len(api_list_all)))
            # print(api_list_all)
            for a in api_list_all:
                api_strings.add(a.function_name)
            
        except:
            pass

    # print(api_strings)
    with open(utopia_anal_result) as f:
        uar = json.load(f)

    real_utipia_api = {}

    for f, p_b in uar["Array"].items():
        f_clean = f.split("(")[0]
        # print(f_clean)
        if f_clean in api_strings and "[" not in f and p_b != -1:
            # print(f"{f_clean} is found!!")

            x1 = f.find("(")
            x2 = f.find(")")
            p_a = f[x1+1:x2]
            
            real_utipia_api[f_clean] = (int(p_a), p_b)

    conds = ConditionManager.instance()

    for f, (p_a, p_b) in real_utipia_api.items():
        cc = conds.conditions.get_function_conditions(f)
        print(f)
        if cc.argument_at[p_a].len_depends_on == f"param_{p_b}":
            print("I have it!")
        else:
            print("I do not have it :(")

    # for x in list(api_per_lib):
    #     l, a = x[0], x[1]
    #     print(f"{l},{a}")

if __name__ == "__main__":
    __main()
