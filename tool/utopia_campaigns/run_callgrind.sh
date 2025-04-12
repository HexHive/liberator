#!/bin/bash

projects=()

if [ $# -ne 0 ]; then
  projects=$@
else
  projects=( "assimp" "libaom" "libvpx" "wabt" ) #"libhtp"
fi



for project in "${projects[@]}"; do

    FUZZ_TARGETS="$(find ./exp_no_asan/${project}/output/fuzzers -maxdepth 1 -type f -executable -printf '%P\n')"

    for fuzz_target in $FUZZ_TARGETS; do
        mkdir -p callgrind/${project}/${fuzz_target}
        CALLGRIND_OUT=./callgrind/${project}/${fuzz_target}
        FUZZ_BINARY=./exp_no_asan/${project}/output/fuzzers/${fuzz_target}
        CORPUS_MIN=./corpus_minimized/${project}/${fuzz_target}
        valgrind --tool=callgrind --callgrind-out-file=${CALLGRIND_OUT}/callgrind.out $FUZZ_BINARY -runs=0 -timeout=100s $CORPUS_MIN
        # apt-get install python3-pip -y
        # pip3 install prof2dot
        gprof2dot --format=callgrind --output=${CALLGRIND_OUT}/out.dot -n0 -e0 --root="*TestBody()" ${CALLGRIND_OUT}/callgrind.out
    done
done
