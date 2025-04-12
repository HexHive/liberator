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

for d in `ls ${DRIVER_FOLDER}/${DRIVER}.cc`
do
    echo "Driver: $d"
    $CXX -g -std=c++11 -fsanitize=fuzzer,address I/${TARGET}/work/include \
    ${TARGET}/work/lib/liburiparser.a -o "${d%%.*}"
done