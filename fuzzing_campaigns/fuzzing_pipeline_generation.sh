#!/bin/bash

if [ -z "$1" ]; then
  CONFIG_NAME="grammar"
else
  CONFIG_NAME=$1
fi

if [ "$2" ]; then
  ONLY_GENERATION=1
fi

export CONF=quickcamp; ./run_analysis.sh

function store_results_to() {
    DEST_FOLDER=$1

    mkdir ${DEST_FOLDER}
    mv workdir_* ${DEST_FOLDER}
    mv config.txt ${DEST_FOLDER}
    mv total_library_coverage* ${DEST_FOLDER}
    if [ -f "time_budget.csv" ]
    then
        mv time_budget.csv ${DEST_FOLDER}
    fi
}

if [ "${ONLY_GENERATION}" ]; then
    GEN24_DEEP0=gen24_deep0_nobias
else
    GEN24_DEEP0=gen24_deep0
fi


# dyn generation for 24 hours and no deep
export CONF=${CONFIG_NAME}; ./run_dynamic_drv_creation.py; ./run_coverage.sh; ./run_coverage.sh comulative; ./get_total_library_coverage.sh;
store_results_to ${GEN24_DEEP0}

if [ "${ONLY_GENERATION}" ]; then
    exit 0
fi

# select best drivers from 18h and deep for 6h
export CONF=${CONFIG_NAME}; ./select_stable_drivers_cluster.py -d ${GEN24_DEEP0} -t 0.75 -k
export CONF=${CONFIG_NAME}; ./run_dynamic_drv_deep.py; ./run_coverage.sh
export CONF=${CONFIG_NAME}; ./cp_coverage_from_generation_phase.py -d ${GEN24_DEEP0} -t 0.75
export CONF=${CONFIG_NAME}; ./run_coverage.sh recalciter; ./get_total_library_coverage.sh; 
store_results_to ${GEN18_DEEP6}

# select best drivers from 12h and deep for 12h
export CONF=${CONFIG_NAME}; ./select_stable_drivers_cluster.py -d ${GEN24_DEEP0} -t 0.5 -k
export CONF=${CONFIG_NAME}; ./run_dynamic_drv_deep.py; ./run_coverage.sh
export CONF=${CONFIG_NAME}; ./cp_coverage_from_generation_phase.py -d ${GEN24_DEEP0} -t 0.5
export CONF=${CONFIG_NAME}; ./run_coverage.sh recalciter; ./get_total_library_coverage.sh; 
store_results_to ${GEN12_DEEP12}

# select best drivers from 6h and deep for 18h
export CONF=${CONFIG_NAME}; ./select_stable_drivers_cluster.py -d ${GEN24_DEEP0} -t 0.25 -k
export CONF=${CONFIG_NAME}; ./run_dynamic_drv_deep.py; ./run_coverage.sh
export CONF=${CONFIG_NAME}; ./cp_coverage_from_generation_phase.py -d ${GEN24_DEEP0} -t 0.25
export CONF=${CONFIG_NAME}; ./run_coverage.sh recalciter; ./get_total_library_coverage.sh; 
store_results_to ${GEN6_DEEP18}
