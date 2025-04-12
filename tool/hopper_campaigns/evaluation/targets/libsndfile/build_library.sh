#!/bin/bash

set -e
set -x

# NOTE: if TOOLD_DIR is unset, I assume to find stuffs in LIBFUZZ folder
if [ -z "$TOOLS_DIR" ]; then
    TOOLS_DIR=$LIBFUZZ
fi

WORK="$TARGET/work"
rm -rf "$WORK"
mkdir -p "$WORK"
mkdir -p "$WORK/lib" "$WORK/include"

WORK_PROFILE="$TARGET/work_profile"
rm -rf "$WORK_PROFILE"
mkdir -p "$WORK_PROFILE"
mkdir -p "$WORK_PROFILE/lib" "$WORK_PROFILE/include"


export LLVM_COMPILER_PATH=$LLVM_DIR/bin
export CC="$LLVM_COMPILER_PATH"/clang
export CXX="$LLVM_COMPILER_PATH"/clang++

echo "make 1"
mkdir -p "$TARGET/repo/libsndfile_build_cov"
cd "$TARGET/repo/libsndfile_build_cov"

# Compile library for coverage
cmake .. -DCMAKE_INSTALL_PREFIX="$WORK_PROFILE" -DBUILD_SHARED_LIBS=on \
        -DENABLE_STATIC=off -DCMAKE_BUILD_TYPE=Debug  -DENABLE_EXTERNAL_LIBS=off \
        -DCMAKE_C_FLAGS_DEBUG="-fprofile-instr-generate -fcoverage-mapping -g" \
        -DCMAKE_CXX_FLAGS_DEBUG="-fprofile-instr-generate -fcoverage-mapping -g"

echo "make clean"
make -j"$(nproc)" clean
echo "make"
make -j"$(nproc)"
echo "make install"
make install


cd ..
mkdir -p "$TARGET/repo/libsndfile_build_fuzz"
cd "$TARGET/repo/libsndfile_build_fuzz"

# Compile library for fuzzing
cmake .. -DCMAKE_INSTALL_PREFIX="$WORK" -DBUILD_SHARED_LIBS=on \
        -DENABLE_STATIC=off -DCMAKE_BUILD_TYPE=Release -DENABLE_EXTERNAL_LIBS=off

echo "make clean"
make -j"$(nproc)" clean
echo "make"
make -j"$(nproc)"
echo "make install"
make install
# configure compiles some shits for testing, better remove it
echo "[INFO] Library installed in: $WORK"
