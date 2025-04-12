import os
import json
import itertools
import sys


def get_max_depth(trace_log):

    with open(trace_log) as f,  open(f'{trace_log}_reverse', 'w') as fout:
        fout.writelines(reversed(f.readlines()))

    trace_log = f'{trace_log}_reverse'
    max_depths_for_functions = {}
    current_test_one_input = 0
    with open(trace_log) as traces_file:
        for line in traces_file:
            line = line.strip()
            if not line.startswith("#"):
                continue
            if "LLVMFuzzerTestOneInput" in line:
                current_test_one_input = int(line.split()[0].lstrip("#"))

            if line.startswith("#0"):
                line_split = line.split()
                if line_split[1].startswith("0x"):
                    function_name = line_split[3].split("(")[0]
                else:
                    function_name = line_split[1]
                if function_name == "(anonymous": #TODO: handle this
                    continue
                if function_name not in max_depths_for_functions:
                    max_depths_for_functions[function_name] = current_test_one_input
                else:
                    max_depths_for_functions[function_name] = max(current_test_one_input, max_depths_for_functions[function_name])

    return max_depths_for_functions


def get_called_apis(trace_log):
    apis = set()
    with open(trace_log) as f:
        for line1, line2, line3, line4, line5 in itertools.zip_longest(*[f]*5):
            if not line5:
                break
            if "TestBody" not in line5:
                continue
            line1, line2, line3, line4, line5 = line1.strip(), line2.strip(), line3.strip(), line4.strip(), line5.strip()
            line5_file_name = line5.split()[-1].split(":")[0]
            for line in [line4, line3, line2, line1]:
                if not line.startswith("#"):
                    break

                file_name = line.split()[-1].split(":")[0]
                if file_name != line5_file_name:
                    line = line.split()
                    if line[2] == "in":
                        apis.add(line[3])
                    else:
                        apis.add(line[1])
                    break
    return apis

# projects = os.listdir("./traces")
# projects = ["assimp", "libaom", "libvpx"]

# result = {}

# for project in projects:
#     result[project] = {}
#     result[project]["stack_depths"] = []
#     fuzzers = os.listdir(f'./traces/{project}')
#     for fuzzer in fuzzers:
#         print(fuzzer)

#         result[project][fuzzer] = {}
#         trace_log =  f"./traces/{project}/{fuzzer}/traces_log"

#         max_depths_for_functions = get_max_depth(trace_log)

#         result[project][fuzzer] = max_depths_for_functions
#         result[project]["stack_depths"] += list(max_depths_for_functions.values())
#         # apis = get_called_apis(trace_log)
#         # result[project][fuzzer]["number_of_apis"] = len(apis)
#         # result[project][fuzzer]["called_apis"] = list(apis)

# with open("max_stack_depth.json", "w+") as write_file:
#     json.dump(result, write_file, indent=4)




if len(sys.argv) != 5:
    print("Need to provide $work_dir $project $fuzz_target $iter")
    exit()

work_dir = sys.argv[1]
project = sys.argv[2]
fuzzer = sys.argv[3]
iteration = sys.argv[4]

trace_log = f"./traces/{work_dir}/{project}/{fuzzer}/iter_{iteration}/traces_log"
max_depths_for_functions = get_max_depth(trace_log)
print(max_depths_for_functions)
print(f"Maximum depth reached: {max(max_depths_for_functions.values())}")