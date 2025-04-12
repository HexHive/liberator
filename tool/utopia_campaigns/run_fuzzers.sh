#!/bin/bash

projects=()

if [ $# -ne 0 ]; then
  projects=$@
else
	projects=( "cpu_features" "libaom" "libhtp" "libvpx" "minijail" "pthreadpool" )
fi

ITERATIONS=1
TIMEOUT=1h

let TOTAL_FUZZERS="$(find exp/*/output/fuzzers -type f -executable | wc -l)*ITERATIONS"


base_dir=$(pwd)
cpu_id=0
counter=0

for i in $( eval echo {1..$ITERATIONS} )
do
    for project in "${projects[@]}"; do
        cd exp/${project}/output/fuzzers

        FUZZ_TARGETS="$(find . -maxdepth 1 -type f -executable -printf '%P\n')"
        cd $base_dir
        for fuzz_target in $FUZZ_TARGETS; do
            mkdir -p crashes_${i}/${project}/${fuzz_target}
            mkdir -p corpus_${i}/${project}/${fuzz_target}

            FUZZ_BINARY=/utopia/exp/${project}/output/fuzzers/${fuzz_target}
            CORPUS=/utopia/corpus_${i}/${project}/${fuzz_target}
            CRASHES=/utopia/crashes_${i}/${project}/${fuzz_target}/

            docker run \
                --rm \
                --cpuset-cpus $cpu_id \
                --privileged \
                --shm-size=2g \
                --platform linux/amd64 \
                -d \
                --name ${fuzz_target}_iter_${i} \
		-v $(pwd):/utopia \
                -t utopia_clang12:latest \
                timeout $TIMEOUT $FUZZ_BINARY $CORPUS -fork=1 -ignore_timeouts=1 -ignore_crashes=1 -ignore_ooms=1 -artifact_prefix=$CRASHES
            cpu_id=$(( cpu_id + 1 ))
            counter=$(( counter + 1 ))

            if [ $cpu_id -eq 15 ]
            then
                echo "Running 15 fuzzers, lets sleep for now"
                echo "Total progress: ${counter}/${TOTAL_FUZZERS}"
                sleep $TIMEOUT
		            cpu_id=0
            fi
        done
    done
    echo "done with run $i"

done
echo "DONE ALL?"
