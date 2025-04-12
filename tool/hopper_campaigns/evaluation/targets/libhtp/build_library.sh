#!/bin/bash
set -e


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
cd "$TARGET/repo"
./autogen.sh
echo "./configure"

# Compile library for coverage
./configure --prefix="$WORK_PROFILE" \
        CXXFLAGS="-fprofile-instr-generate -fcoverage-mapping -g" \
        CFLAGS="-fprofile-instr-generate -fcoverage-mapping -g"

echo "make clean"
make -j$(nproc) clean
echo "make"
make -j$(nproc)
echo "make install"
make install

echo "make clean"
make -j$(nproc) clean



# Compile library for fuzzing
./configure --prefix="$WORK" \
        --disable-debug 

echo "make"
make -j$(nproc)
echo "make install"
make install

echo "[INFO] Library installed in: $WORK"
