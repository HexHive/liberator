#!/bin/bash


projects=()

if [ $# -ne 0 ]; then
  projects=$@
else
  projects=( "cpu_features" "libaom" "libvpx" "libhtp" "minijail" "pthreadpool" )
fi


for i in {1..3}; do
for project in "${projects[@]}"; do

    FUZZ_TARGETS="$(find ./exp/${project}/output/profiles -maxdepth 1 -type f -executable -printf '%P\n')"
    PROJECT_COVERAGE=./coverage_data/${project}/iter_${i}
    SOURCES="$(find ./exp/${project} -iname '*.h' -or -iname '*.cpp' -or -iname '*.c' -or -iname '*.cc')"
    for fuzz_target in $FUZZ_TARGETS; do

        FUZZ_BINARY=./exp/${project}/output/fuzzers/${fuzz_target}
        PROFILE_BINARY=./exp/${project}/output/profiles/${fuzz_target}

        mkdir -p corpus_minimized/${project}/iter_${i}/${fuzz_target}
        mkdir -p coverage_data/${project}/iter_${i}/${fuzz_target}
        COVERAGE=./coverage_data/${project}/iter_${i}/${fuzz_target}
        CORPUS_MIN=./corpus_minimized/${project}/iter_${i}/${fuzz_target}
        CORPUS=./corpus_{i}/${project}/${fuzz_target}


        $FUZZ_BINARY -merge=1 $CORPUS_MIN $CORPUS
        LLVM_PROFILE_FILE="${fuzz_target}.profraw" $PROFILE_BINARY -runs=0 $CORPUS_MIN
        mv ${fuzz_target}.profraw $PROJECT_COVERAGE
        llvm-profdata-12 merge -sparse $PROJECT_COVERAGE/${fuzz_target}.profraw -o $PROJECT_COVERAGE/${fuzz_target}.profdata
        llvm-cov-12 show $PROFILE_BINARY -instr-profile=$PROJECT_COVERAGE/${fuzz_target}.profdata > show
        llvm-cov-12 report $PROFILE_BINARY -instr-profile=$PROJECT_COVERAGE/${fuzz_target}.profdata > report
        llvm-cov-12 report -show-functions $PROFILE_BINARY -instr-profile=$PROJECT_COVERAGE/${fuzz_target}.profdata $SOURCES > functions
        #llvm-cov-12 export -format=text $PROFILE_BINARY -instr-profile=$PROJECT_COVERAGE/${fuzz_target}.profdata > export.json
        mv show $COVERAGE
        mv report $COVERAGE
        mv functions $COVERAGE
        #mv export.json $COVERAGE
        # python3 -m json.tool export.json > exp.json
        # mv exp.json $COVERAGE
        # rm export.json
        echo "Done with ${fuzz_target}"
    done

    # Get aggregated coverage of all fuzzers for a project
    OBJECTS=""
    for fuzz_target in $FUZZ_TARGETS; do
        llvm-profdata-12 merge -sparse $PROJECT_COVERAGE/*.profdata -o $PROJECT_COVERAGE/merged.profdata
        PROFILE_BINARY=./exp/${project}/output/profiles/${fuzz_target}
        if [[ -z $OBJECTS ]]; then
            # The first object needs to be passed without -object= flag.
            OBJECTS="$PROFILE_BINARY"
        else
            OBJECTS="$OBJECTS -object=$PROFILE_BINARY"
        fi
    done

    llvm-cov-12 show $OBJECTS -instr-profile=$PROJECT_COVERAGE/merged.profdata > show
    llvm-cov-12 report $OBJECTS -instr-profile=$PROJECT_COVERAGE/merged.profdata > report
    llvm-cov-12 report -show-functions $OBJECTS -instr-profile=$PROJECT_COVERAGE/merged.profdata $SOURCES > functions
    mv show $PROJECT_COVERAGE
    mv report $PROJECT_COVERAGE
    mv functions $PROJECT_COVERAGE

    echo "Done project ${project}"
done
done
rm -f crash-* 2> /dev/null
rm -f leak-* 2> /dev/null
rm -f oom-* 2> /dev/null
rm -f slow-unit-* 2> /dev/null
# rm -rf corpus_minimized

echo "DONE"

