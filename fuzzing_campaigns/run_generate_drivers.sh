#!/bin/bash

source campaign_configuration.sh

mv ../overwrite.toml ../overwrite_backup.toml
mv ../workdir ../workdir_backup 2> /dev/null

for ndrivers in "${NUM_OF_DRIVERS[@]}"; do
    for napis in "${NUM_OF_APIs[@]}"; do

        mkdir -p workdir_${ndrivers}_${napis}
        for project in "${PROJECTS[@]}"; do

            echo "[generator]" > ../overwrite.toml
            echo "pool_size = ${ndrivers}" >> ../overwrite.toml
            echo "driver_size = ${napis}" >> ../overwrite.toml
            echo "num_seeds = ${NUM_OF_SEEDS}" >> ../overwrite.toml
            echo "policy = \"${POLICY}\"" >> ../overwrite.toml
            echo "bias = \"${BIAS}\"" >> ../overwrite.toml

            if [ ${USE_CUSTOM_APIS} -eq 1 ]; then
                echo "[analysis]" >> ../overwrite.toml
                echo "minimum_apis = \"/workspaces/libfuzz/targets/${project}/custom_apis_minized.txt\"" >> ../overwrite.toml
            fi

            export TARGET=$project
            ../docker/run_drivergeneration.sh

            # Dirty way to compile all drivers
            export TIMEOUT=0
            ../docker/run_fuzzing.sh
            rm -Rf workdir_${ndrivers}_${napis}/${project} || true
            mv ../workdir/${project} workdir_${ndrivers}_${napis}/${project}
        done
    done
done

mv ../overwrite_backup.toml ../overwrite.toml
mv ../workdir_backup ../workdir 2> /dev/null

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