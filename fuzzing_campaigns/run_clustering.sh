#!/bin/bash -e


source campaign_configuration.sh

IMG_NAME="libpp-clustering"
LIBPP=../



for project in "${PROJECTS[@]}"; do
    set -x
    DOCKER_BUILDKIT=1 docker build \
        --build-arg USER_UID=$(id -u) --build-arg GROUP_UID=$(id -g) \
        --build-arg target_name="$project" \
        -t "${IMG_NAME}-${project}" --target libfuzzpp_crash_cluster \
        -f "$LIBPP/Dockerfile" "$LIBPP"
    set +x
done


echo "[INFO] Running: $IMG_NAME"


for ndrivers in "${NUM_OF_DRIVERS[@]}"; do
    for napis in "${NUM_OF_APIs[@]}"; do        
        for project in "${PROJECTS[@]}"; do

            if [[ -z ${GRAMMAR_MODE} ]]; then

                PROJECT_WORKDIR="./workdir_${ndrivers}_${napis}/${project}"
                DRIVER_FOLDER="${PROJECT_WORKDIR}/drivers"
                if [ -d "$DRIVER_FOLDER" ]; then
                    DRIVER_NAMES="$(find ${DRIVER_FOLDER} -type f -executable)"
                else 
                    continue
                fi
                CRASHES=${PROJECT_WORKDIR}/crashes
                
                for i in $( eval echo {1..$ITERATIONS} ); do
                    for driver_name in $DRIVER_NAMES; do
                        driver_name=$(basename $driver_name)
                        rm -Rf ${CRASHES}/${driver_name} || true
                        mkdir -p ${CRASHES}/${driver_name}

                        DRIVER_CRASHES="${PROJECT_WORKDIR}/results/iter_${i}/crashes/${driver_name}"
                        [ "$(ls -A ${DRIVER_CRASHES})" ] \
                            && cp ${DRIVER_CRASHES}/* ${CRASHES}/${driver_name} || echo "No crashes for ${project}/${driver_name} on iter ${i}"
                    done
                done

                PROJECT_FOLDER="/workspaces/libfuzz/fuzzing_campaigns/workdir_${ndrivers}_${napis}/${project}"
                docker run --privileged --env TARGET=${project} \
                        --env TARGET_WORKDIR=${PROJECT_FOLDER} \
                        --env GRAMMAR_MODE=${GRAMMAR_MODE} \
                        -v $(pwd)/..:/workspaces/libfuzz "${IMG_NAME}-${project}" || true

            else

                for i in $( eval echo {1..$ITERATIONS} ); do

                    PROJECT_WORKDIR="./workdir_${ndrivers}_${napis}/${project}/iter_${i}"
                    DRIVER_FOLDER="${PROJECT_WORKDIR}/drivers"
                    if [ -d "$DRIVER_FOLDER" ]; then
                        DRIVER_NAMES="$(find ${DRIVER_FOLDER} -type f -executable)"
                    else 
                        continue
                    fi
                    # CRASHES=${PROJECT_WORKDIR}/iter_${i}/crashes
                    
                    for driver_name in $DRIVER_NAMES; do
                        driver_name=$(basename $driver_name)
                        # rm -Rf ${CRASHES}/${driver_name} || true
                        # mkdir -p ${CRASHES}/${driver_name}

                        DRIVER_CRASHES="${PROJECT_WORKDIR}/crashes/${driver_name}"
                        if [ "$(ls -A ${DRIVER_CRASHES})" ]; then
                            # && cp ${DRIVER_CRASHES}/* ${CRASHES}/${driver_name} || 

                            PROJECT_FOLDER="/workspaces/libfuzz/fuzzing_campaigns/workdir_${ndrivers}_${napis}/${project}/iter_${i}"
                            docker run --privileged --env TARGET=${project} \
                                    --env TARGET_WORKDIR=${PROJECT_FOLDER} \
                                    --env GRAMMAR_MODE=${GRAMMAR_MODE} \
                                    -v $(pwd)/..:/workspaces/libfuzz "${IMG_NAME}-${project}" || true
                        else
                            echo "No crashes for ${project}/${driver_name} on iter ${i}"
                        fi
                    done

                done

            fi
        done
    done
done
