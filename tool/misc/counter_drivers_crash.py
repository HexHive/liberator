#!/usr/bin/python

import sys, os
import pathlib


cluster = sys.argv[1]

drivers_lib = {}

def get_driver(path):
    # "ExecutablePath": "/workspaces/libfuzz/fuzzing_campaigns/workdir_40_32/cjson/cluster_drivers/driver21_cluster"
    with open(path) as f:
        for l in f:
            if "ExecutablePath" in l:
                dd = l.strip().split(":")[1][1:-2]
                return dd

    return ""

print(cluster)
for l in os.listdir(cluster):
    drivers_lib[l] = set()

    # print(l)
    o = pathlib.Path(os.path.join(cluster,l,"clusters"))
    for pp in o.rglob("*"):
        p = str(pp.absolute())
        
        if not p.endswith(".casrep"):
            continue

        if "clerr" in p:
           continue

        # print(p)
        driver = get_driver(p)
        drivers_lib[l].add(driver)
    # not in clerr

for l in sorted(drivers_lib.keys()):
    d = drivers_lib[l]
    tot = len(d)
    print(f"{l}: {tot}")