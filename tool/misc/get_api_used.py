#!/usr/bin/env python3

import os, json, argparse

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
    n_apis = []
    n_drivers = set()

    workdirs = set()
    for x in os.listdir(root_dir):
        if x.startswith(workdir_token):
            workdirs.add(os.path.join(root_dir, x))
            n_driver, n_api = x.replace(workdir_token, "").split("_")
            n_apis += [int(n_api)]
            n_drivers.add(int(n_driver))
    
    for w in workdirs:
        for l in os.listdir(w):
            libs.add(l)
    
    
    stats = {}
    for l in libs:
        for a in n_apis:
            for d in n_drivers:
                base_fold = f"{workdir_token}{d}_"    
                ll = stats.get(l, set())
                stats[l] = ll
                for i in range(d):
                    fp = os.path.join(root_dir, f"{base_fold}{a}", l, "metadata", f"driver{i}.meta")
                    if os.path.isfile(fp):
                        with open(fp, "r") as f:
                            md = json.load(f)
                        am = md["api_multiset"]
                        for au in am.keys():
                            stats[l].add(au)

    if summary:
        for l, s in stats.items():
            print(f"{l}: {len(s)}")
    else:
        for l, s in stats.items():
            print(f"{l}: {s}")

if __name__ == "__main__":
    _main()