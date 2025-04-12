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
echo "cmake"
mkdir -p "$TARGET/repo/pthreadpool_cov"
cd "$TARGET/repo/pthreadpool_cov"
# Compile library for coverage
cmake .. -DCMAKE_INSTALL_PREFIX=$WORK_PROFILE -DBUILD_SHARED_LIBS=on \
	-DCMAKE_BUILD_TYPE=Debug \
        -DCMAKE_C_FLAGS_DEBUG="-fprofile-instr-generate -fcoverage-mapping -g" \
        -DCMAKE_CXX_FLAGS_DEBUG="-fprofile-instr-generate -fcoverage-mapping -g" \
        -DBENCHMARK_ENABLE_GTEST_TESTS=off \
        -DBENCHMARK_ENABLE_INSTALL=off

echo "make clean"
make -j$(nproc) clean
echo "make"
make -j$(nproc)
echo "make install"
make install

cd ..
mkdir -p "$TARGET/repo/pthreadpool_fuzz"
cd "$TARGET/repo/pthreadpool_fuzz"


cmake .. -DCMAKE_INSTALL_PREFIX=$WORK -DBUILD_SHARED_LIBS=on \
        -DBENCHMARK_ENABLE_GTEST_TESTS=off \
        -DBENCHMARK_ENABLE_INSTALL=off

echo "make clean"
make -j$(nproc) clean
echo "make"
make -j$(nproc)
echo "make install"
make install


echo "[INFO] Library installed in: $WORK"
