#!/usr/bin/env python3

import os, json, argparse
import matplotlib.pyplot as plt

tot_api = {
    "pthreadpool":30,
    "libaom":47,
    "zlib":88,
    "c-ares":126,
    "cpu_features":7,
    "libpcap":88,
    "cjson":78,
    "libvpx":35,
    'libtiff':197,
    "minijail":97
}               
                

def _main():
    
    parser = argparse.ArgumentParser(description='APIs used over time')
    parser.add_argument('-totapi', '-t', type=str, required=True, help='Tot API per library')
    parser.add_argument('-usedapi', '-u', type=str, required=True, help='API Used')
    
    args = parser.parse_args()
    
    totapi = args.totapi
    usedapi = args.usedapi
    
    tot_api = {}
    
    with open(totapi) as fp_tot:
        for l in fp_tot:
            if "WARNING" in l:
                continue
            
            l = l.strip()
            # print(l)
            
            target, func = l.split(",")
            
            xx = tot_api.get(target, set())
            
            xx |= set([func.split(":")[0]])
            
            tot_api[target] = xx
            
    used_api = {}
    with open(usedapi) as fp_used:
        for l in fp_used:
            
            # if "cpu_features" in l:
            #     from IPython import embed; embed(); exit(1)
            
            l = l.strip()
            
            target, x = l.split(":")
            
            x = x[3:-2].split("', '")
            
            # x = [a.strip()[1:-1] for a in x]
            
            used_api[target] = set(x)
            
            # print(x)
            # exit(1)
        
    nonused = {}    
    for t in tot_api.keys():
        tot = tot_api[t]
        used = used_api[t]
        nonused[t] = tot - used
        
    
    with open("unused_api.txt", "w") as fp:
        for t, funs in nonused.items():
            fp.write(f"{t} ({len(funs)}) :\n")
            for f in funs:
                fp.write(f + "\n")
            fp.write("="*30 + "\n")
            
        
    
if __name__ == "__main__":
    _main()