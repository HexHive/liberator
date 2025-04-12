#!/bin/bash

${LIBFUZZ}/targets/${TARGET_NAME}/compile_driver.sh

if [ "$TIMEOUT" -eq "0" ]; then
	echo "No Timeout, just compile"
	exit 0
fi

if [ -z $RESULTS_FOLDER ]; then
    RESULTS_FOLDER=${LIBFUZZ}/workdir/${TARGET_NAME}
fi

echo "[INFO] DRIVER_FOLDER: ${DRIVER_FOLDER}"

for d in `find ${DRIVER_FOLDER} -type f -executable -name "${DRIVER}"`
do
    echo $d
    DRIVER_NAME=$(basename $d)
    echo "Fuzzing ${TIMEOUT}: ${DRIVER_NAME}"
    DRIVER_CORPUS=${RESULTS_FOLDER}/corpus/${DRIVER_NAME}
    DRIVER_CORNEW=${RESULTS_FOLDER}/corpus_new/${DRIVER_NAME}
    CRASHES_DIR=${RESULTS_FOLDER}/crashes/${DRIVER_NAME}
    rm -Rf ${CRASHES_DIR} || true
    rm -Rf ${DRIVER_CORNEW} || true
    mkdir -p ${CRASHES_DIR}
    mkdir -p ${DRIVER_CORNEW}

    # make a copy of initial corpus
    cp -r ${DRIVER_CORPUS}/* ${DRIVER_CORNEW}/

    # # THIS IS WITH STANDARD MODE -- STOP AT THE FIRST CRASHE
    # timeout $TIMEOUT $d ${DRIVER_CORPUS} \
    #     -artifact_prefix=${CRASHES_DIR}/ || echo "Done: $d"

    # echo "COV_PLATEAU_TIMEOUT: ${COV_PLATEAU_TIMEOUT}"
    echo "FORK_MODE: ${FORK_MODE}"

    if [[ ${FORK_MODE} -eq 0 || -z ${FORK_MODE} ]]; then
        (sleep $TIMEOUT && pkill ${DRIVER_NAME}) &
        $d ${DRIVER_CORNEW} -artifact_prefix=${CRASHES_DIR}/ -ignore_crashes=1 \
            -ignore_timeouts=1 -ignore_ooms=1 -detect_leaks=0 || echo "Done: $d"
        pkill -9 $d
    else
        timeout -k 10s $TIMEOUT \
        $d ${DRIVER_CORNEW} -artifact_prefix=${CRASHES_DIR}/ -ignore_crashes=1 \
            -ignore_timeouts=1 -ignore_ooms=1 -detect_leaks=0 -fork=1
    fi

    
done
