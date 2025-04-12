#!/usr/bin/env python3

import os, json, shutil, filecmp, tempfile
from subprocess import STDOUT, check_output


MAX_TIMEOUT = 60*5
COND_EXTRACTOR = "/workspaces/libfuzz/condition_extractor/bin/extractor"


def read_api_file(api_file):
    api_list = []
    with open(api_file) as f:
        for l in f:
            if l is not None:
                json_api = json.loads(l)
                api_list += [json_api["function_name"]]

    return api_list


def run_test(api_file, bc_file, expected_output_folder):
    temp_dir = tempfile.mkdtemp()
    api_list = read_api_file(api_file)

    n_api_list = len(api_list)

    print(f"[INFO] Found {n_api_list} APIs")

    for i, api in enumerate(api_list):
        print(f"[{i+1}/{n_api_list}] Doing {api}")
        api_output = os.path.join(temp_dir, f"{api}.json")
        correct_output = os.path.join(expected_output_folder, f"{api}.json")

        # ./bin/extractor /workspaces/libfuzz/analysis/libtiff/work/lib/libtiff.a.bc -function ${FUNCTION_NAME} -output  ${FUNCTION_NAME}.json -t json 
        cmd = [COND_EXTRACTOR, bc_file, "-function", api, "-output",  api_output, "-t", "json"]
        check_output(cmd, stderr=STDOUT, timeout=MAX_TIMEOUT)
        
        if filecmp.cmp(correct_output, api_output):
            print("PASS")
        else:
            print("FAIL")
            with open(correct_output) as f1:
                with open(api_output) as f2:
                    print(f"Expected Output: {f1.read()}")
                    print(f"Actual Output: {f2.read()}")

    print("[DONE] all tests PASS")
    shutil.rmtree(temp_dir)


def _main():
    tests_directory = os.path.dirname(os.path.realpath(__file__))
    tests = [f.path for f in os.scandir(tests_directory) if f.is_dir() and "test_" in f.path]
    
    for test in tests:
        test_name = test.split("/")[-1]
        print(f"RUNNING TESTS FOR {test_name}")
        print("-----------------------------------------------")
        api_file = os.path.join(test, "apis_llvm.json")        
        bc_file = os.path.join(test, ".library.o.bc")

        if not os.path.exists(api_file) or not os.path.exists(bc_file):
            os.chdir(test)
            check_output(["make", "clean"], stderr=STDOUT, timeout=MAX_TIMEOUT)
            check_output(["make"], stderr=STDOUT, timeout=MAX_TIMEOUT)
        expected_outputs = os.path.join(test, "expected_outputs")
        run_test(api_file, bc_file, expected_outputs)
        print("-----------------------------------------------")


if __name__ == "__main__":
    _main()
