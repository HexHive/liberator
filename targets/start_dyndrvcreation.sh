#!/bin/bash

# export TARGET_NAME=${TARGET}
# export TARGET=${LIBFUZZ}/analysis/${TARGET}
# ENV TARGET_NAME ${target_name}

convert_to_seconds() {
    local time_string="$1"
    local seconds=0
    
    # Loop through each character in the time string
    while [[ -n "$time_string" ]]; do
        local num=${time_string%[a-zA-Z]*}  # Extract the number from the string
        local unit=${time_string##*[0-9]}    # Extract the unit from the string
        
        case "$unit" in
            "s") seconds=$((seconds + num));;
            "m") seconds=$((seconds + num * 60));;
            "h") seconds=$((seconds + num * 3600));;
        esac
        
        time_string=${time_string#*[a-zA-Z]}  # Remove the processed part from the string
    done
    
    echo "$seconds"
}

# echo "[TOOLS_DIR] ${TOOLS_DIR}"
echo "[TARGET] ${TARGET}"

if [ -z ${RESULTS_FOLDER} ]; then
    RESULTS_FOLDER=${LIBFUZZ}/workdir/${TARGET_NAME}
    export DRIVER_FOLDER=${LIBFUZZ}/workdir/${TARGET_NAME}/drivers
fi

if [ -z ${DRIVER_FOLDER} ]; then
    export DRIVER_FOLDER="${RESULTS_FOLDER}/drivers"
fi

mkdir -p ${RESULTS_FOLDER}

echo ${DRIVER_FOLDER}
echo ${RESULTS_FOLDER}
echo "wait..."
sleep 10s

LOGS_ID=$(date +%s%N | cut -b1-13)
SERVICE_LOG="service_${LOGS_ID}.log"
OVERWRITE_FILE="${LIBFUZZ}/overwrite_${LOGS_ID}.toml"

# taken from env?
echo "[generator]" > ${OVERWRITE_FILE}
echo "pool_size = 1" >> ${OVERWRITE_FILE}
echo "driver_size = 1" >> ${OVERWRITE_FILE}
echo "num_seeds = 1" >> ${OVERWRITE_FILE}
echo "policy = \"${POLICY}\"" >> ${OVERWRITE_FILE}
echo "workdir = \"${RESULTS_FOLDER}\"" >> ${OVERWRITE_FILE}

${LIBFUZZ}/tool/service.py \
    --config ${LIBFUZZ}/targets/${TARGET_NAME}/generator.toml \
    --overwrite ${OVERWRITE_FILE} &> ${SERVICE_LOG} & 


# http://127.0.0.1:5000 -- localhost
SERVICE_ENDPOINT="http://127.0.0.1:5000"

SRV_TO_START=5s
# echo "[INFO] Wait ${SRV_TO_START} till service bootsrap"
# sleep ${SRV_TO_START}
until curl --output /dev/null --silent --head --fail ${SERVICE_ENDPOINT}; do
    echo "[INFO] Waiting for driver generator service (${SRV_TO_START})"
    sleep ${SRV_TO_START}
done

# # NOTE: these env vars must be set in Dockerfile
# export DRIVER_FOLDER=${LIBFUZZ}/workdir/${TARGET_NAME}/drivers
# export CORPUS_FOLDER=${LIBFUZZ}/workdir/${TARGET_NAME}/corpus_new
# export LLVM_DIR=/usr

loop_duration=$(convert_to_seconds ${WHOLE_TIMEOUT})
echo "[INFO] whole fuzzing campaing is ${loop_duration}s"
echo "[INFO] single driver is ${TIMEOUT}"

start_time=$(date +%s)

export FEEDBACK=${RESULTS_FOLDER}/feedback.txt
# 60s w/o new seeds? let's change...
export COV_PLATEAU_TIMEOUT=30
# this tells start_fuzz_driver to use libfuzzer in fork-mode
export FORK_MODE=1

while true
do
    current_time=$(date +%s)
    time_passed=$((current_time - start_time))
    if [ $time_passed -ge $loop_duration ]; then
        echo "[INFO] Loop duration reached. Exiting loop."
        break
    fi

    export DRIVER=$(curl http://127.0.0.1:5000/get_new_driver 2> /dev/null)
    echo "[INFO] Get driver $DRIVER"
    ${LIBFUZZ}/targets/start_fuzz_driver.sh &> /dev/null
    echo "[INFO] Send feedback to the driver generator"
    CAUSE_DRIVER_STOP=$(sed '1q;d' ${FEEDBACK})
    DRIVER_EXEC_TIME=$(sed '2q;d' ${FEEDBACK})
    curl http://127.0.0.1:5000/push_feedback?driver=${DRIVER}\&time=${DRIVER_EXEC_TIME}\&cause=${CAUSE_DRIVER_STOP}\&time_plateau=${COV_PLATEAU_TIMEOUT} &> /dev/null

    # to save some space, I delete the drivers that do not contribute to new coverage
    if [[ $(ls ${RESULTS_FOLDER}/corpus_new/${DRIVER} | wc -l) -eq 1 ]]; then
        rm ${RESULTS_FOLDER}/drivers/${DRIVER}
        rm ${RESULTS_FOLDER}/profiles/${DRIVER}_profile 
        rm ${RESULTS_FOLDER}/cluster_drivers/${DRIVER}_cluster 
    fi

done

# get statistics about the corred and failed paths observed
curl http://127.0.0.1:5000 > ${RESULTS_FOLDER}/paths_observed.txt

## FLAVIO: zsh is for debug
# zsh

# bloddy way to kill the service w no mercy
# kill -9 $(lsof -i :5000 | awk 'NR > 1 {print $2}')

mv ${SERVICE_LOG} ${RESULTS_FOLDER}/service.log
mv ${OVERWRITE_FILE} ${RESULTS_FOLDER}/overwrite.toml
