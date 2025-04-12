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
make -j$(nproc) PREFIX=$WORK/include OS=linux ARCH=x86_64 V=No install

echo "make 1"
cd "$TARGET/repo"
        
echo "make clean"
make -j$(nproc) clean
echo "make"
make -j$(nproc) PREFIX=$WORK/include OS=linux ARCH=x86_64 V=No install

echo "[INFO] Library installed in: $WORK"
