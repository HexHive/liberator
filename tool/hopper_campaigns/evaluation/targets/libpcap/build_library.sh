#!/bin/bash

set -e
set -x


WORK="$TARGET/work"
rm -rf "$WORK"
mkdir -p "$WORK"
mkdir -p "$WORK/lib" "$WORK/include"

WORK_PROFILE="$TARGET/work_profile"
rm -rf "$WORK_PROFILE"
mkdir -p "$WORK_PROFILE"
mkdir -p "$WORK_PROFILE/lib" "$WORK_PROFILE/include"

export CC=clang
export CXX=clang++

echo "make 1"
mkdir -p "$TARGET/repo/pcap_build_cov"
cd "$TARGET/repo/pcap_build_cov"

# Compile library for coverage
cmake .. -DCMAKE_INSTALL_PREFIX="$WORK_PROFILE" -DBUILD_SHARED_LIBS=on \
        -DCMAKE_BUILD_TYPE=Debug \
        -DCMAKE_C_FLAGS_DEBUG="-fprofile-instr-generate -fcoverage-mapping -g" \
        -DCMAKE_CXX_FLAGS_DEBUG="-fprofile-instr-generate -fcoverage-mapping -g"

echo "make clean"
make -j"$(nproc)" clean
echo "make"
make -j"$(nproc)"
echo "make install"
make install


# Compile library for fuzzing
cmake .. -DCMAKE_INSTALL_PREFIX="$WORK" -DBUILD_SHARED_LIBS=on \
        -DCMAKE_BUILD_TYPE=Release 

echo "make clean"
make -j"$(nproc)" clean
echo "make"
make -j"$(nproc)"
echo "make install"
make install
# configure compiles some shits for testing, better remove it
echo "[INFO] Library installed in: $WORK"
