#!/usr/bin/env python3

import argparse, os

def _main():
    parser = argparse.ArgumentParser(description='Spurious crashes')
    parser.add_argument('-rootdir', '-d', type=str, help='Driver Folder', required=True)

    args = parser.parse_args()
    
    rootdir = args.rootdir
    
    sum_crashes = {}
    
    for l in os.listdir(rootdir):
        extract_ok = False
        if l.startswith("workdir_"):
            n_driver = 0
            # n_api = 0
            try:
                n_driver, _ = l.split("_")[1:]
                n_driver = int(n_driver)
                extract_ok = True
            except:
                pass
            
            for t in os.listdir(os.path.join(rootdir, l)):
                n_crashes = sum_crashes.get(t, 0)
                n_iter = len(os.listdir(os.path.join(rootdir, l, t, "results")))
                for i in range(1, n_iter + 1):
                    for d in range(n_driver):
                        n_crashes += len(os.listdir(os.path.join(rootdir, l, t, "results", f"iter_{i}", "crashes", f"driver{d}")))
                                
                sum_crashes[t] = n_crashes
            
        if not extract_ok:
            continue
        
        # print(l)
        
    for t, s in dict(sorted(sum_crashes.items())).items():
        print(f"{t}: {s}")
    
if __name__ == "__main__":
    _main()