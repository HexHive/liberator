#!/usr/bin/env python3

import os, json, argparse

def find_meta_files(directory):
    meta_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.meta'):
                meta_files.append(os.path.join(root, file))
    return meta_files

def _main():

    parser = argparse.ArgumentParser(description='Counts the API used')
    parser.add_argument('-root', '-r', type=str, help='Report File', required=True, default="/media/hdd0/libfuzz_scratchpad/main/fuzzing_campaigns")
    parser.add_argument('-summary', '-s', help='Summary', required=False, action='store_true')
    
    args = parser.parse_args()
    
    root_dir = args.root
    # libs =  "cpu_features libtiff minijail pthreadpool libaom libvpx libhtp libpcap c-ares zlib cjson".split()
    # libs =  "cjson".split()
    libs = set()
    summary = args.summary

    workdir_token = "workdir_"

    # n_drivers = 40
    # apis = [2, 4, 8, 16, 32]

    workdirs = set()
    for x in os.listdir(root_dir):
        if x.startswith(workdir_token):
            workdirs.add(os.path.join(root_dir, x))
            # n_driver, n_api = x.replace(workdir_token, "").split("_")
            # n_apis += [n_api]
            # n_drivers.add(n_driver)
    
    for w in workdirs:
        for l in os.listdir(w):
            libs.add(l)
    
    stats = {}
    stats_f = {}
    for l in libs:
        base_fold = f"{workdir_token}X_X"    
        ll = stats.get(l, set())
        stats[l] = ll
        ll2 = stats_f.get(l, 0)
        stats_f[l] = ll2
        meta_path = os.path.join(root_dir, f"{base_fold}", l)
        for m in find_meta_files(meta_path):
            if os.path.isfile(m):
                with open(m, "r") as f:
                    md = json.load(f)
                am = md["api_multiset"]
                for au in am.keys():
                    stats[l].add(au)
                for k, f in am.items():
                    stats_f[l] += f

    if summary:
        for l, s in stats.items():
            print(f"{l}: {len(s)}")
        for l, s in stats_f.items():
            print(f"{l}: {s}")
    else:
        for l, s in stats.items():
            print(f"{l}: {s}")

if __name__ == "__main__":
    _main()
