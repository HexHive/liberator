#!/bin/bash

projects=()

export ASAN_SYMBOLIZER_PATH=$(which llvm-symbolizer)
export MSAN_SYMBOLIZER_PATH=$(which llvm-symbolizer)


if [ $# -ne 0 ]; then
  projects=$@
else
  projects=( "cpu_features" "libaom" "libhtp" "libvpx" "minijail" "pthreadpool" )
fi


for project in "${projects[@]}"; do
  FUZZ_TARGETS="$(find ./exp/${project}/output/fuzzers -maxdepth 1 -type f -executable -printf '%P\n')"
  for fuzz_target in $FUZZ_TARGETS; do

    FUZZ_BINARY=./exp/${project}/output/fuzzers/${fuzz_target}
    CRASHES=./crashes/${project}/${fuzz_target}
    casr-libfuzzer -i $CRASHES -o ../triaging/utopia/${project}/${fuzz_target} -- $FUZZ_BINARY &> ./triage_logs/${project}_${fuzz_target}_triage
  done
done
