#!/bin/bash

# set -x
# set -e

# BLUE='\033[0;34m'
# WHITE='\033[0;37m' 
# RED='\033[0;31m'  
# GREEN='\033[0;32m'

cd ../../fuzzing_campaigns/

export CONF=regtest
./run_analysis.sh
./run_generate_drivers.sh

all_exec=$(find workdir_*_*/*/drivers -type f -executable | wc -l)
all_drvr=$(find workdir_*_*/*/drivers -type f -name "*.cc" | wc -l)

compiled_drivers=0
if [[ "${all_exec}" -eq "${all_drvr}" ]]; then
    echo -e "[OK] All drivers are compiled!" 
else
    non_cmp=$(($all_drvr-$all_exec))
    echo -e "[ERROR] ${non_cmp} drivers not compile!"
    compiled_drivers=1
fi

export CONF=regtest
source campaign_configuration.sh

empty_projects=()
for project in "${PROJECTS[@]}"; do
    for ndrivers in "${NUM_OF_DRIVERS[@]}"; do
        for napis in "${NUM_OF_APIs[@]}"; do
            PROJECT_FOLDER="./workdir_${ndrivers}_${napis}/${project}"
            # echo ${PROJECT_FOLDER}
            if [ -z "$(ls -A ${PROJECT_FOLDER}/drivers)" ]; then
                empty_projects=( ${empty_projects[@]} ${PROJECT_FOLDER} )
            fi
        done
    done
done

empty_folders_check=0
if [[ "${#empty_projects[@]}" -ne 0 ]]; then
    echo -e "[ERROR] ${#empty_projects[@]} working dirs are empty:"
    for dir in "${empty_projects[@]}"; do
        echo ${dir}
    done 
    empty_folders_check=1
else
    echo "[OK] ${#empty_projects[@]} working dirs are empty:"
fi

if [[ "${compiled_drivers}" -ne 0 || "${empty_folders_check}" -ne 0 ]]; then
    echo "[ERROR] in driver compilations"
    exit 1
else
    echo "[OK] all drivers correctly generated!"
fi

echo "Clean workdir folders"
rm -Rf workdir_*_*/

cd -