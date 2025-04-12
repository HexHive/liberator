#!/bin/bash
set -e

##
# Pre-requirements:
# - env TARGET: path to target work dir
# - env OUT: path to directory where artifacts are stored
# - env CC, CXX, FLAGS, LIBS, etc...
##

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

CFLAGS_BASE=$CFLAGS
CXXFLAGS_BASE=$CXXFLAGS

# Compile library for coverage
export CFLAGS=$CFLAGS_BASE" -fprofile-instr-generate -fcoverage-mapping -g"
export CXXFLAGS=$CXXFLAGS_BASE" -fprofile-instr-generate -fcoverage-mapping -g"

echo "make clean"
make -j$(nproc) clean
echo "make"
make -j$(nproc) OUT="$WORK/lib" 


# Compile library for fuzzing
export CFLAGS=$CFLAGS_BASE
export CXXFLAGS=$CXXFLAGS_BASE

echo "make clean"
make -j$(nproc) clean
echo "make"
make -j$(nproc) OUT="$WORK/lib" 
cp *.h $WORK/include

echo "[INFO] Library installed in: $WORK"
