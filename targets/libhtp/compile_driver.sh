#!/bin/bash
set -e

##
# Pre-requirements:
# - env TARGET: path to target work dir
# - env OUT: path to directory where artifacts are stored
# - env CC, CXX, FLAGS, LIBS, etc...
##

# if [ ! -d "$TARGET/repo" ]; then
#     echo "fetch.sh must be executed first."
#     exit 1
# fi

WORK="$TARGET/work"

cd "$TARGET/repo"

CXX=$LLVM_DIR/bin/clang++
CC=$LLVM_DIR/bin/clang

echo "Compiling: ${DRIVER_FOLDER}/${DRIVER}.cc"
PROFILE_DRIVERS="${DRIVER_FOLDER}"/../profiles
mkdir -p $PROFILE_DRIVERS
CLUSTER_DRIVERS="${DRIVER_FOLDER}"/../cluster_drivers
mkdir -p $CLUSTER_DRIVERS

# [TAG] FIRST LOOP FOR COMPILATION!!!
for d in `ls ${DRIVER_FOLDER}/${DRIVER}.cc`
do
    echo "Driver: $d"
    DRIVER_NAME=$(basename $d)

    # [TAG] THIS STEP MUST BE ADAPTED FOR EACH LIBRARY
    # Compile driver for fuzzing
    $CXX -std=c++11 -fsanitize=fuzzer,address -I/${TARGET}/work/include \
        $d -Wl,--whole-archive ${TARGET}/work/lib/libhtp.a -Wl,--no-whole-archive -lz -ljpeg -llzma -Wl, \
        -Bdynamic -lstdc++ -o "${d%%.*}" || true
    
    # Compile driver for clustering
    $CXX -g -std=c++11 -fsanitize=fuzzer,address -I/${TARGET}/work/include \
        $d -Wl,--whole-archive ${TARGET}/work/lib/libhtp_cluster.a -Wl,--no-whole-archive -lz -ljpeg -llzma -Wl, \
        -Bdynamic -lstdc++ -o "${CLUSTER_DRIVERS}/${DRIVER_NAME%%.*}_cluster" || true

    # Compile driver for coverage
    $CXX -g -std=c++11 -fsanitize=fuzzer -fprofile-instr-generate -fcoverage-mapping \
        -I/${TARGET}/work/include $d -Wl,--whole-archive ${TARGET}/work/lib/libhtp_profile.a -Wl,--no-whole-archive -lz -ljpeg -llzma -Wl, \
        -Bdynamic -lstdc++ -o "${PROFILE_DRIVERS}/${DRIVER_NAME%%.*}_profile" || true
done
