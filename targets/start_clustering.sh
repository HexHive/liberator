#!/bin/bash


echo "[INFO] CLUSTERING: ${TARGET_NAME}"

source "$HOME/.cargo/env"

DRIVER_FOLDER=${TARGET_WORKDIR}/cluster_drivers
CRASHES=${TARGET_WORKDIR}/crashes
OUTPUT=${TARGET_WORKDIR}/clusters
LOGS=${OUTPUT}/logs

FUZZ_TARGETS="$(find ${DRIVER_FOLDER} -type f -executable)"

export ASAN_SYMBOLIZER_PATH=${LLVM_DIR}/bin/llvm-symbolizer

echo $DRIVER_FOLDER

if [[ $TOTAL_LIBRARY_CLUSTER ]]; then

    CLUSTER_FILTER=misc/cluster_filter.txt

    TARGET_FOLDER=fuzzing_campaigns/total_library_cluster/${TARGET_NAME}
    TARGET_CRASHES=${TARGET_FOLDER}/crashes
    TARGET_CLUSTERS=${TARGET_FOLDER}/clusters

    mkdir -p ${TARGET_CRASHES}
    mkdir -p ${TARGET_CLUSTERS}

    echo "serach .casrep here ${OUTPUT}"
    find ${OUTPUT} -name "*.casrep" -exec cp {} ${TARGET_CRASHES} \;

    casr-cluster --ignore ${CLUSTER_FILTER} -c ${TARGET_CRASHES} ${TARGET_CLUSTERS} || true

    exit 0
fi

rm -Rf $OUTPUT $LOGS || true
mkdir -p $OUTPUT $LOGS

for d in $FUZZ_TARGETS
do
    DRIVER_NAME=$(basename $d)
    DRIVER_NAME=${DRIVER_NAME/_cluster/}
    echo "CLUSTERING: ${DRIVER_NAME} -i ${CRASHES}/${DRIVER_NAME} -o ${OUTPUT}/${DRIVER_NAME}"
    casr-libfuzzer -i ${CRASHES}/${DRIVER_NAME} -o ${OUTPUT}/${DRIVER_NAME} -- $d &> ${LOGS}/${DRIVER_NAME}
done
