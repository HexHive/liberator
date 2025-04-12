import sys

if len(sys.argv) != 5:
    print("Need to provide $work_dir $project $fuzz_target $iter")
    exit()

work_dir = sys.argv[1]
project = sys.argv[2]
fuzzer = sys.argv[3]
itereration = sys.argv[4]



functions = set()
function_coverage = f'./{work_dir}/{project}/coverage_data/{fuzzer}/functions'
with open(function_coverage) as function_coverage:
    for line in function_coverage:
        line = line.strip()
        if not line:
            continue
        if line.startswith("File") or line.startswith("Name") or line.startswith("TOTAL") or line.startswith("-"):
            continue

        line = line.split()
        if line[1] == line[2]:
            continue
        # if "fuzzargsprofile" not in line[0].lower() and "autofuzz" not in line[0].lower() and "test" not in line[0].lower():
        functions.add(line[0])

gdb_script = f'''
set pagination off

set logging file ./traces/{work_dir}/{project}/{fuzzer}/iter_{itereration}/traces_log
set logging on

file ./{work_dir}/{project}/profiles/{fuzzer}_profile

'''

for function in functions:
    gdb_script += \
f'''
break {function}
commands
bt
continue
end
'''

gdb_script += \
f'''
set $_exitcode = -999

run -runs=0 -ignore_crashes=1 ./{work_dir}/{project}/results/iter_{itereration}/corpus_mini/{fuzzer}

if $_exitcode != -999
    quit
end
'''

with open(f'./traces/{work_dir}/{project}/{fuzzer}/iter_{itereration}/gdb_commands', 'w+') as f:
    f.write(gdb_script)
