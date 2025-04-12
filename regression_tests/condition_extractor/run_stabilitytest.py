#!/usr/bin/env python3

import sys, os, argparse, json, shutil
from subprocess import STDOUT, check_output

def read_api_file(api_file):
    # print("reading  api file...")

    api_list = []

    with open(api_file) as f:
        for l in f:
            if l is not None:
                json_api = json.loads(l)
                api_list += [json_api["function_name"]]

    return api_list

# 5 minutes timeout
MAX_TIMEOUT = 60*5
COND_EXTRACTOR = "/workspaces/libfuzz/condition_extractor/bin/extractor"
OUTPUT_FOLDER = "constrains_output" 

def _main():
    parser = argparse.ArgumentParser(description='Run stability process of condition_extractor.')
    parser.add_argument('--api_file', type=str, required=True, help='File listing APIs to test')
    parser.add_argument('--bc_file', type=str, required=True, help='LLVM BC file to analyze')

    args = parser.parse_args()

    api_list = read_api_file(args.api_file)

    bc_file = args.bc_file

    # create new outpuf folder anytime
    if os.path.exists(OUTPUT_FOLDER):
        shutil.rmtree(OUTPUT_FOLDER)
    os.makedirs(OUTPUT_FOLDER)

    n_api_list = len(api_list)

    print(f"[INFO] Found {n_api_list} APIs")

    for i, api in enumerate(api_list):
        print(f"[{i}/{n_api_list}] Doing {api}")
        api_output = os.path.join(OUTPUT_FOLDER, f"{api}.json")

        # ./bin/extractor /workspaces/libfuzz/analysis/libtiff/work/lib/libtiff.a.bc -function ${FUNCTION_NAME} -output  ${FUNCTION_NAME}.json -t json 
        cmd = [COND_EXTRACTOR, bc_file, "-function", api, "-output",  api_output, "-t", "json"]
        output = check_output(cmd, stderr=STDOUT, timeout=MAX_TIMEOUT)


    print("[DONE]")

if __name__ == "__main__":
    _main()
