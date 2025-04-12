#!/bin/bash

source campaign_configuration.sh


IMG_NAME="fuzzing_campaigns"
set -x
# # FLAVIO: this block makes sure to recompile LLVM and make it available for the next script
# DOCKER_BUILDKIT=1 docker build --target libfuzzpp_dev_image -f ../Dockerfile ..
# docker run -v $(pwd)/..:/workspaces/libfuzz libfuzzpp_dev_image \
#     /workspaces/lib

for project in "${PROJECTS[@]}"; do
    DOCKER_BUILDKIT=1 docker build \
        --build-arg USER_UID=$(id -u) --build-arg GROUP_UID=$(id -g) \
        --build-arg target_name="$project" \
        -t "$IMG_NAME-$project" --target libfuzzpp_fuzzing \
        -f "../Dockerfile" "../"
    set +x
done

let TOTAL_FUZZERS="$(find workdir_*_*/*/drivers/ -type f -executable | wc -l)*ITERATIONS"
COUNTER=0
CPU_ID=0

# if needed, load custom timebudget per library from select_stable_drivers.py
if [ ${USE_PER_LIBRARY_TIMEBUDGET} -eq 1 ]; then
    declare -A TIMEOUT_PER_LIBRARY
    while IFS='|' read -r key value; do
        TIMEOUT_PER_LIBRARY[$key]=$value
    done < time_budget.csv
    TIMEOUT_SYNC=-1s
else
    TIMEOUT_SYNC=${TIMEOUT}
fi

for ndrivers in "${NUM_OF_DRIVERS[@]}"; do
    for napis in "${NUM_OF_APIs[@]}"; do
        for i in $( eval echo {1..$ITERATIONS} ); do
            for project in "${PROJECTS[@]}"; do
                PROJECT_FOLDER="./workdir_${ndrivers}_${napis}/${project}"
                DRIVER_FOLDER="${PROJECT_FOLDER}/drivers"
                RESULTS_FOLDER="${PROJECT_FOLDER}/results/iter_${i}"
                FUZZ_TARGETS="$(find ${DRIVER_FOLDER} -maxdepth 1 -type f -executable -printf '%P\n')"

                if [ ${USE_PER_LIBRARY_TIMEBUDGET} -eq 1 ]; then
                    TIMEOUT=${TIMEOUT_PER_LIBRARY[$project]}
                    if [[ ${TIMEOUT_SYNC::-1} -eq "-1" ]] || [[ ${TIMEOUT::-1} -gt ${TIMEOUT_SYNC::-1} ]]; then
                        TIMEOUT_SYNC=${TIMEOUT}
                    fi
                fi

                for fuzz_target in $FUZZ_TARGETS; do
                    if [[ ${TIMEOUT_SYNC::-1} -eq "-1" ]]; then
                        TIMEOUT_SYNC=${TIMEOUT}
                    fi
                    echo "Fuzzing ./workdir_${ndrivers}_${napis}/${project}/${fuzz_target} [${i}/${ITERATIONS}] w/ t.o. ${TIMEOUT}"

                    DRIVER_CORPUS=${PROJECT_FOLDER}/corpus/${fuzz_target}
                    DRIVER_CORNEW=${RESULTS_FOLDER}/corpus_new/${fuzz_target}
                    CRASHES_DIR=${RESULTS_FOLDER}/crashes/${fuzz_target}
                    rm -Rf ${CRASHES_DIR} || true
                    rm -Rf ${DRIVER_CORNEW} || true
                    mkdir -p ${CRASHES_DIR}
                    mkdir -p ${DRIVER_CORNEW}
                    cp -r ${DRIVER_CORPUS}/* ${DRIVER_CORNEW}/

                    FUZZ_BINARY=/libfuzzpp/${DRIVER_FOLDER}/${fuzz_target}
                    FUZZ_CORPUS=/libfuzzpp/$DRIVER_CORNEW
                    CRASHES=/libfuzzpp/$CRASHES_DIR

                    docker run \
                        --rm \
                        --cpuset-cpus $CPU_ID \
                        -d \
                        --name ${project}_${fuzz_target}_${ndrivers}_${napis}_${i} \
                        -v $(pwd):/libfuzzpp \
                        --mount type=tmpfs,destination=/tmpfs \
                        -t "$IMG_NAME-$project" \
                        timeout -k 10s $TIMEOUT $FUZZ_BINARY $FUZZ_CORPUS -artifact_prefix=${CRASHES}/ -ignore_crashes=1 -ignore_timeouts=1 -ignore_ooms=1 -detect_leaks=0 -fork=1
                    COUNTER=$(( COUNTER + 1 ))
                    CPU_ID=$(( CPU_ID + 1 ))
                    if [ $CPU_ID -eq $MAX_CPUs ];
                    then
                        echo "Running ${MAX_CPUs} fuzzers in parallel, sleeping for ${TIMEOUT_SYNC}"
                        echo "Total progress: ${COUNTER}/${TOTAL_FUZZERS}"
                        sleep $TIMEOUT_SYNC
                        CPU_ID=0
                        if [ ${USE_PER_LIBRARY_TIMEBUDGET} -eq 1 ]; then
                            TIMEOUT_SYNC=-1s
                        fi
                    fi
                done
            done
        done
    done
done

SPARE_FUZZERS=$(( COUNTER % MAX_CPUs ))
if [ $SPARE_FUZZERS -ne 0 ]
then
    echo "Running ${SPARE_FUZZERS} fuzzers in parallel, sleeping for ${TIMEOUT_SYNC}"
    echo "Total progress: ${COUNTER}/${TOTAL_FUZZERS}"
    sleep $TIMEOUT_SYNC
fi
