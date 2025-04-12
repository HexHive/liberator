#!/bin/bash
set -e

##
# Pre-requirements:
# - env TARGET: path to target work dir
# - env OUT: path to directory where artifacts are stored
# - env CC, CXX, FLAGS, LIBS, etc...
##

# export TARGET=/tmp/libtiff

if [ ! -d "$TARGET/repo" ]; then
    echo "fetch.sh must be executed first."
    exit 1
fi

export CC=$LLVM_DIR/bin/clang
export CXX=$LLVM_DIR/bin/clang++

WORK="$TARGET/work"
rm -rf "$WORK"
mkdir -p "$WORK"
mkdir -p "$WORK/lib" "$WORK/include"

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
make -j$(nproc) OUT="$WORK/lib" CC_STATIC_LIBRARY\(libminijail.pie.a\)

mv $WORK/lib/libminijail.pie.a $WORK/lib/libminijail_profile.pie.a


# Compile library for debugging
export CFLAGS=$CFLAGS_BASE" -fsanitize=fuzzer-no-link,address -g"
export CXXFLAGS=$CXXFLAGS_BASE" -fsanitize=fuzzer-no-link,address -g"

echo "make clean"
make -j$(nproc) clean
echo "make"
make -j$(nproc) OUT="$WORK/lib" CC_STATIC_LIBRARY\(libminijail.pie.a\)

mv $WORK/lib/libminijail.pie.a $WORK/lib/libminijail_cluster.pie.a


# Compile library for fuzzing
export CFLAGS=$CFLAGS_BASE" -fsanitize=fuzzer-no-link,address"
export CXXFLAGS=$CXXFLAGS_BASE" -fsanitize=fuzzer-no-link,address"

echo "make clean"
make -j$(nproc) clean
echo "make"
make -j$(nproc) OUT="$WORK/lib" CC_STATIC_LIBRARY\(libminijail.pie.a\)
cp *.h $WORK/include

echo "[INFO] Library installed in: $WORK"
