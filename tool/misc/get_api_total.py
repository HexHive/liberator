#!/usr/bin/env python3

PROJECT_FOLDER="/workspaces/libfuzz"

import sys, os
sys.path.append(PROJECT_FOLDER)

import argparse
from framework import * 
from generator import Configuration
import logging


def __main():
    
    parser = argparse.ArgumentParser(description='Get all APIs for each library')
    parser.add_argument('--targets', '-t', type=str, help='Targets folder', required=True)

    parser.add_argument('--summary', '-s',  action='store_true', help='If indicated, list all functions and their arguments/return values')

    args = parser.parse_args()

    targets = args.targets
    summary = args.summary
    libs = set()

    api_per_lib = set()
    all_api = set()

    for t in os.listdir(targets):
        ft = os.path.join(targets, t)
        config_path = os.path.join(targets, t, "generator.toml")
        if os.path.isdir(ft) and os.path.isfile(config_path):
            try:
                config = Configuration(config_path)
                api_list_all = config.api_list_all

                if summary:
                    api_per_lib.add((t, len(api_list_all)))
                else:
                    for a in api_list_all:
                        fun_name = a.function_name
                        for i, arg in enumerate(a.arguments_info):
                            all_api.add(f"{t},{fun_name}:{i}")

                        all_api.add(f"{t},{fun_name}:-1")

            except:
                pass

    
    if summary:
        for x in api_per_lib:
            l, n = x[0], x[1]
            print(f"{l}:{n}")
    else:
        for x in sorted(all_api):
            print(x)

if __name__ == "__main__":
    __main()
