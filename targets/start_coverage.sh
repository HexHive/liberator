#!/bin/bash

echo "[INFO] COVERAGE METRICS: ${TARGET_NAME}"


REPO="/home/libfuzz/library/repo"

if [[ -z ${TOTAL_DRIVER_COVERAGE_COMULATIVE} ]] && [[ -z ${RECALC_COV_ITER} ]]; then
    rm -Rf ${PROJECT_COVERAGE} || true
fi
mkdir -p ${PROJECT_COVERAGE}

SOURCES="$(find $REPO -iname '*.h' -or -iname '*.cpp' -or -iname '*.c' -or -iname '*.cc')"
if [[ -z ${GRAMMAR_MODE} ]]; then
    DRIVER_PATH_REGEX="\/workspaces\/libfuzz\/workdir\/.*\/drivers\/.*\.cc"
else
    DRIVER_PATH_REGEX="\/workspaces\/libfuzz\/fuzzing_campaigns\/workdir_X_X\/${TARGET_NAME}/iter_.*\/drivers\/.*\.cc"
fi


if [[ $TOTAL_LIBRARY_COVERAGE ]]; then

    if [[ -z ${GRAMMAR_MODE} ]]; then
        MERGED_PROFDATAS="$(ls -d fuzzing_campaigns/*/${TARGET_NAME}/coverage_data/iter_*/merged.profdata)"
        PROFILES="$(ls -d fuzzing_campaigns/*/${TARGET_NAME}/profiles/*_profile)"
    else
        MERGED_PROFDATAS="$(ls -d fuzzing_campaigns/*/${TARGET_NAME}/iter_*/coverage_data/merged.profdata)"
        PROFILES="$(ls -d fuzzing_campaigns/*/${TARGET_NAME}/iter_*/profiles/*_profile)"
    fi

    mkdir -p fuzzing_campaigns/total_library_coverage/${TARGET_NAME}
    ${LLVM_DIR}/bin/llvm-profdata merge -sparse $MERGED_PROFDATAS -o fuzzing_campaigns/total_library_coverage/${TARGET_NAME}/merged.profdata

    OBJECTS=""
    for profile in $PROFILES; do
        if [[ -z $OBJECTS ]]; then
            # The first object needs to be passed without -object= flag.
            OBJECTS="$profile"
        else
            OBJECTS="$OBJECTS -object=$profile"
        fi
    done

    ${LLVM_DIR}/bin/llvm-cov show $OBJECTS -instr-profile=fuzzing_campaigns/total_library_coverage/${TARGET_NAME}/merged.profdata > fuzzing_campaigns/total_library_coverage/${TARGET_NAME}/show
    ${LLVM_DIR}/bin/llvm-cov report $OBJECTS -instr-profile=fuzzing_campaigns/total_library_coverage/${TARGET_NAME}/merged.profdata -ignore-filename-regex=$DRIVER_PATH_REGEX > fuzzing_campaigns/total_library_coverage/${TARGET_NAME}/report
    ${LLVM_DIR}/bin/llvm-cov report -show-functions $OBJECTS -instr-profile=fuzzing_campaigns/total_library_coverage/${TARGET_NAME}/merged.profdata $SOURCES -ignore-filename-regex=$DRIVER_PATH_REGEX > fuzzing_campaigns/total_library_coverage/${TARGET_NAME}/functions

    for i in $( eval echo {1..$ITERATIONS} ); do
        TARGET_ITER=fuzzing_campaigns/total_library_coverage/${TARGET_NAME}/iter_${i}

        if [[ -z ${GRAMMAR_MODE} ]]; then
            MERGED_PROFDATAS="$(ls -d fuzzing_campaigns/*/${TARGET_NAME}/coverage_data/iter_${i}/merged.profdata)"
        else
            MERGED_PROFDATAS="$(ls -d fuzzing_campaigns/*/${TARGET_NAME}/iter_${i}/coverage_data/merged.profdata)"
        fi

        mkdir -p ${TARGET_ITER}
        ${LLVM_DIR}/bin/llvm-profdata merge -sparse $MERGED_PROFDATAS -o ${TARGET_ITER}/merged.profdata

        ${LLVM_DIR}/bin/llvm-cov show $OBJECTS -instr-profile=${TARGET_ITER}/merged.profdata > ${TARGET_ITER}/show
        ${LLVM_DIR}/bin/llvm-cov report $OBJECTS -instr-profile=${TARGET_ITER}/merged.profdata -ignore-filename-regex=$DRIVER_PATH_REGEX > ${TARGET_ITER}/report
        ${LLVM_DIR}/bin/llvm-cov report -show-functions $OBJECTS -instr-profile=${TARGET_ITER}/merged.profdata $SOURCES -ignore-filename-regex=$DRIVER_PATH_REGEX > ${TARGET_ITER}/functions

    done

    exit 0
fi

if [[ $TOTAL_DRIVER_COVERAGE_COMULATIVE ]]; then
    FUZZ_TARGETS="$(find ${DRIVER_FOLDER} -type f -executable)"    
    mapfile -t FUZZ_TARGETS_ARR <<< "${FUZZ_TARGETS[@]}"

    # Sort the array by extracting the number at the end of each string
    SORTED_DRIVERS=($(for driver in "${FUZZ_TARGETS_ARR[@]}"; do num=$(echo "$driver" | grep -o '[0-9]*$'); echo "$num $driver"; done | sort -n | awk '{print $2}'))

    PROFDATA_COMULATIVE=()
    OBJECTS=""
    for d in ${SORTED_DRIVERS[@]}; do
        DRIVER_NAME=$(basename $d)

        # workdir_X_X/cpu_features/iter_1/drivers/driver0 -> $d
        # workdir_X_X/cpu_features/iter_1/coverage_data/driver0.profdata

        # Step 1: Replace 'drivers' with 'coverage_data'
        d_profdata="${d/drivers/coverage_data}.profdata"

        PROFDATA_COMULATIVE+=("${d_profdata}")

        DRIVER_COVERAGE_COMULATIVE=${PROJECT_COVERAGE}/${DRIVER_NAME}_comulative.profdata

        ${LLVM_DIR}/bin/llvm-profdata merge -sparse ${PROFDATA_COMULATIVE[@]} -o ${DRIVER_COVERAGE_COMULATIVE}

        PROFILE_BINARY=${DRIVER_FOLDER}/../profiles/${DRIVER_NAME}_profile
        if [[ -z ${OBJECTS} ]]; then
            # The first object needs to be passed without -object= flag.
            OBJECTS="$PROFILE_BINARY"
        else
            OBJECTS="$OBJECTS -object=${PROFILE_BINARY}"
        fi

        if [[ -z ${GRAMMAR_MODE} ]]; then
            echo "TODO: not implemented yet"
            exit 0
            # TODO: not sure I need this in non-grammar mode
            # ${LLVM_DIR}/bin/llvm-cov show $PROFILE_BINARY -instr-profile=$PROJECT_COVERAGE/${DRIVER_NAME}.profdata > $DRIVER_COVERAGE/show
            # ${LLVM_DIR}/bin/llvm-cov report $OBJECTS -instr-profile=${d_profdata} -ignore-filename-regex=$DRIVER_PATH_REGEX > ${PROJECT_COVERAGE}/${DRIVER_NAME}/report_comulative
            # ${LLVM_DIR}/bin/llvm-cov report -show-functions $PROFILE_BINARY -instr-profile=$PROJECT_COVERAGE/${DRIVER_NAME}.profdata $SOURCES -ignore-filename-regex=$DRIVER_PATH_REGEX > $DRIVER_COVERAGE/functions
            # ${LLVM_DIR}/bin/llvm-cov export -format=text $PROFILE_BINARY -instr-profile=$PROJECT_COVERAGE/${DRIVER_NAME}.profdata > $DRIVER_COVERAGE/export.json
        else
            # TODO: tail -n 1 report text and remove it
            ${LLVM_DIR}/bin/llvm-cov report $OBJECTS -instr-profile=${DRIVER_COVERAGE_COMULATIVE} -ignore-filename-regex=$DRIVER_PATH_REGEX > ${PROJECT_COVERAGE}/${DRIVER_NAME}/report_comulative
            mv ${PROJECT_COVERAGE}/${DRIVER_NAME}/report_comulative ${PROJECT_COVERAGE}/${DRIVER_NAME}/report_old
            tail -n 1 ${PROJECT_COVERAGE}/${DRIVER_NAME}/report_old > ${PROJECT_COVERAGE}/${DRIVER_NAME}/report_comulative
            rm ${PROJECT_COVERAGE}/${DRIVER_NAME}/report_old
        fi

    done
    exit 0
fi

if [[ $TOTAL_DRIVER_COVERAGE ]]; then
    DRIVER_FOLDER=${PROJECT_FOLDER}/drivers
    FUZZ_TARGETS="$(find ${DRIVER_FOLDER} -type f -executable)"
    for d in $FUZZ_TARGETS; do
        DRIVER_NAME=$(basename $d)
        if [[ -z ${GRAMMAR_MODE} ]]; then
            DRIVER_PROFDATAS="$(ls -d ${PROJECT_FOLDER}/coverage_data/iter_*/${DRIVER_NAME}.profdata)"
        else
            DRIVER_PROFDATAS="$(ls -d ${PROJECT_FOLDER}/iter_*/coverage_data/${DRIVER_NAME}.profdata)"
        fi
        mkdir -p ${PROJECT_FOLDER}/coverage_data/${DRIVER_NAME}
        ${LLVM_DIR}/bin/llvm-profdata merge -sparse $DRIVER_PROFDATAS -o ${PROJECT_FOLDER}/coverage_data/${DRIVER_NAME}/merged.profdata

        if [[ -z ${GRAMMAR_MODE} ]]; then

            PROFILE_BINARY=${PROJECT_FOLDER}/profiles/${DRIVER_NAME}_profile

            ${LLVM_DIR}/bin/llvm-cov show $PROFILE_BINARY -instr-profile=${PROJECT_FOLDER}/coverage_data/${DRIVER_NAME}/merged.profdata > ${PROJECT_FOLDER}/coverage_data/${DRIVER_NAME}/show
            ${LLVM_DIR}/bin/llvm-cov report $PROFILE_BINARY -instr-profile=${PROJECT_FOLDER}/coverage_data/${DRIVER_NAME}/merged.profdata -ignore-filename-regex=$DRIVER_PATH_REGEX > ${PROJECT_FOLDER}/coverage_data/${DRIVER_NAME}/report
            ${LLVM_DIR}/bin/llvm-cov report -show-functions $PROFILE_BINARY -instr-profile=${PROJECT_FOLDER}/coverage_data/${DRIVER_NAME}/merged.profdata $SOURCES -ignore-filename-regex=$DRIVER_PATH_REGEX > ${PROJECT_FOLDER}/coverage_data/${DRIVER_NAME}/functions
        fi
    done
    exit 0
fi

if [[ $TOTAL_LIBRARY_COVERAGE_FOR_CONFIGURATION ]]; then
    if [[ -z ${GRAMMAR_MODE} ]]; then
        MERGED_PROFDATAS="$(ls -d ${PROJECT_FOLDER}/coverage_data/iter_*/merged.profdata)"
        PROFILES="$(ls -d ${PROJECT_FOLDER}/profiles/*_profile)"
    else
        MERGED_PROFDATAS="$(ls -d ${PROJECT_FOLDER}/iter_*/coverage_data/merged.profdata)"
        PROFILES="$(ls -d ${PROJECT_FOLDER}/iter_*/profiles/*_profile)"
    fi    
    mkdir -p ${PROJECT_FOLDER}/coverage_data/total
    ${LLVM_DIR}/bin/llvm-profdata merge -sparse $MERGED_PROFDATAS -o ${PROJECT_FOLDER}/coverage_data/total/merged.profdata

    OBJECTS=""
    for profile in $PROFILES; do
        if [[ -z $OBJECTS ]]; then
            # The first object needs to be passed without -object= flag.
            OBJECTS="$profile"
        else
            OBJECTS="$OBJECTS -object=$profile"
        fi
    done

    ${LLVM_DIR}/bin/llvm-cov show $OBJECTS -instr-profile=${PROJECT_FOLDER}/coverage_data/total/merged.profdata > ${PROJECT_FOLDER}/coverage_data/total/show
    ${LLVM_DIR}/bin/llvm-cov report $OBJECTS -instr-profile=${PROJECT_FOLDER}/coverage_data/total/merged.profdata -ignore-filename-regex=$DRIVER_PATH_REGEX > ${PROJECT_FOLDER}/coverage_data/total/report
    ${LLVM_DIR}/bin/llvm-cov report -show-functions $OBJECTS -instr-profile=${PROJECT_FOLDER}/coverage_data/total/merged.profdata $SOURCES -ignore-filename-regex=$DRIVER_PATH_REGEX > ${PROJECT_FOLDER}/coverage_data/total/functions

    exit 0
fi

FUZZ_TARGETS="$(find ${DRIVER_FOLDER} -type f -executable)"
if [[ -z ${RECALC_COV_ITER} ]]; then
    for d in $FUZZ_TARGETS
    do
        echo $d
        DRIVER_NAME=$(basename $d)
        echo "COVERAGE: ${DRIVER_NAME}"

        DRIVER_COVERAGE=${PROJECT_COVERAGE}/${DRIVER_NAME}
        DRIVER_COR=${CORPUS_FOLDER}/${DRIVER_NAME}
        # if [[ -z ${GRAMMAR_MODE} ]]; then
        mkdir -p $DRIVER_COVERAGE
        # fi

        PROFILE_BINARY=${DRIVER_FOLDER}/../profiles/${DRIVER_NAME}_profile

        INPUTS="$(ls $DRIVER_COR)"
        for input in $INPUTS; do
            LLVM_PROFILE_FILE="${DRIVER_NAME}-${input}.profraw" timeout -k 10s 1m $PROFILE_BINARY -runs=0 $DRIVER_COR/$input
            # the coverage produces a timeout, we might consider it as a timeout crash
            if [[ $? -ne 0 ]]; then
                echo "[INFO] Error while computing the coverage, moving to crashes"
                CRASH_FOLDER="${CORPUS_FOLDER/corpus_new/crashes}"
                cp $DRIVER_COR/$input ${CRASH_FOLDER}/${DRIVER_NAME}/coverr-$input
            fi
            mv ${DRIVER_NAME}-${input}.profraw $PROJECT_COVERAGE
        done

        ${LLVM_DIR}/bin/llvm-profdata merge -sparse $PROJECT_COVERAGE/${DRIVER_NAME}-*.profraw -o $PROJECT_COVERAGE/${DRIVER_NAME}.profdata
        rm -f $PROJECT_COVERAGE/${DRIVER_NAME}-*.profraw
        if [[ -z ${GRAMMAR_MODE} ]]; then
            ${LLVM_DIR}/bin/llvm-cov show $PROFILE_BINARY -instr-profile=$PROJECT_COVERAGE/${DRIVER_NAME}.profdata > $DRIVER_COVERAGE/show
            ${LLVM_DIR}/bin/llvm-cov report $PROFILE_BINARY -instr-profile=$PROJECT_COVERAGE/${DRIVER_NAME}.profdata -ignore-filename-regex=$DRIVER_PATH_REGEX > $DRIVER_COVERAGE/report
            ${LLVM_DIR}/bin/llvm-cov report -show-functions $PROFILE_BINARY -instr-profile=$PROJECT_COVERAGE/${DRIVER_NAME}.profdata $SOURCES -ignore-filename-regex=$DRIVER_PATH_REGEX > $DRIVER_COVERAGE/functions
            ${LLVM_DIR}/bin/llvm-cov export -format=text $PROFILE_BINARY -instr-profile=$PROJECT_COVERAGE/${DRIVER_NAME}.profdata > $DRIVER_COVERAGE/export.json
        else
            # TODO: tail -n 1 report text and remove it
            ${LLVM_DIR}/bin/llvm-cov report $PROFILE_BINARY -instr-profile=$PROJECT_COVERAGE/${DRIVER_NAME}.profdata -ignore-filename-regex=$DRIVER_PATH_REGEX > $DRIVER_COVERAGE/report
            mv $DRIVER_COVERAGE/report $DRIVER_COVERAGE/report_old
            tail -n 1 $DRIVER_COVERAGE/report_old > $DRIVER_COVERAGE/report
            rm $DRIVER_COVERAGE/report_old
        fi
    done
fi

OBJECTS=""
for d in $FUZZ_TARGETS; do
    ${LLVM_DIR}/bin/llvm-profdata merge -sparse $PROJECT_COVERAGE/*.profdata -o $PROJECT_COVERAGE/merged.profdata
    DRIVER_NAME=$(basename $d)
    PROFILE_BINARY=${DRIVER_FOLDER}/../profiles/${DRIVER_NAME}_profile
    if [[ -z $OBJECTS ]]; then
        # The first object needs to be passed without -object= flag.
        OBJECTS="$PROFILE_BINARY"
    else
        OBJECTS="$OBJECTS -object=$PROFILE_BINARY"
    fi
done
${LLVM_DIR}/bin/llvm-cov show $OBJECTS -instr-profile=$PROJECT_COVERAGE/merged.profdata > $PROJECT_COVERAGE/show
${LLVM_DIR}/bin/llvm-cov report $OBJECTS -instr-profile=$PROJECT_COVERAGE/merged.profdata -ignore-filename-regex=$DRIVER_PATH_REGEX > $PROJECT_COVERAGE/report
${LLVM_DIR}/bin/llvm-cov report -show-functions $OBJECTS -instr-profile=$PROJECT_COVERAGE/merged.profdata $SOURCES -ignore-filename-regex=$DRIVER_PATH_REGEX > $PROJECT_COVERAGE/functions
