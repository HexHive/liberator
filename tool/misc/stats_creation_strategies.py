#!/usr/bin/env python3

PROJECT_FOLDER="/workspaces/libfuzz"

import sys, os
sys.path.append(PROJECT_FOLDER)

import argparse
from framework import * 
from generator import Configuration
from common import DataLayout
from constraints import ConditionManager
from driver.factory import Factory
from driver.ir import PointerType
import logging

bannedtypes = ["unsignedchar", "FILE"]

def __main():
    
    parser = argparse.ArgumentParser(description='Show creation strategies for each type')
    parser.add_argument('--targets', '-t', type=str, help='Targets folder', required=True)
    parser.add_argument('--target_name', '-n', type=str, help='Target project', required=False, default="")

    args = parser.parse_args()

    targets = args.targets
    target_name = args.target_name
    
    for t in os.listdir(targets):
        if target_name != "" and target_name != t:
            continue
        
        t_name = t
        
        ft = os.path.join(targets, t_name)
        config_path = os.path.join(targets, t_name, "generator.toml")
        if os.path.isdir(ft) and os.path.isfile(config_path):
            try:
                config = Configuration(config_path)
                config.build_data_layout()
                config.build_condition_manager()
                
                dl = DataLayout.instance()
                cm = ConditionManager.instance()
                
                init_per_type = dict()
                for i, ii_a in cm.init_per_type.items():
                    ii = [x[0] for x in ii_a]
                    if isinstance(i, PointerType):
                        init_per_type[i.get_base_type()] = ii
                    else:
                        init_per_type[i] = ii
                        
                set_per_type = dict()
                for i, ii in cm.set_per_type.items():
                    ii = [x[0] for x in ii_a]
                    if isinstance(i, PointerType):
                        set_per_type[i.get_base_type()] = ii
                    else:
                        set_per_type[i] = ii
                
                types = set()
                
                for x, _ in dl.layout.items():
                    
                    ptr_str = 0
                    flag = "ref"
                    if dl.is_a_pointer(x) and x[-1] == "*":
                        ptr_str = x.count("*") 
                        x = x[:-ptr_str]
                        
                    if x in bannedtypes:
                        continue
                    
                    if dl.is_a_struct(x):
                        t = Factory.normalize_type(x, 64, flag, [False] * (ptr_str + 1) )
                        types.add(t)
                        
                with open(f"{t_name}.txt", "w") as out_f:
                            
                    for t in types:
                        something = False
                        print(f"{t}", file=out_f)
                        if t in cm.source_per_type:
                            print("Sources:", file=out_f)
                            for s in cm.source_per_type[t]:
                                print(f"\t{s}", file=out_f)
                            something = True
                        if dl.is_fuzz_friendly(t.token):
                            print("Trivial", file=out_f)
                            something = True
                        if t in init_per_type:
                            print("Init:", file=out_f)
                            for i in init_per_type[t]:
                                print(f"\t{i}", file=out_f)
                            something = True
                        if t in set_per_type:
                            print("Set:", file=out_f)
                            for s in set_per_type[t]:
                                print(f"\t{s}", file=out_f)
                            something = True
                        if not something:
                            print("Nothing", file=out_f)
                        print(file=out_f)
                            
                # from IPython import embed; embed(); exit(1)
                
            except:
                pass    
    
if __name__ == "__main__":
    __main()
