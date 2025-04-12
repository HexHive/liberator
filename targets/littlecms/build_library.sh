#!/bin/bash
set -e

##
# Pre-requirements:
# - env TARGET: path to target work dir
# - env OUT: path to directory where artifacts are stored
# - env CC, CXX, FLAGS, LIBS, etc...
##

# export TARGET=/tmp/liblcms2

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
./autogen.sh
echo "./configure"

# Compile library for coverage
./configure --disable-shared --prefix="$WORK" \
        CXXFLAGS="-fprofile-instr-generate -fcoverage-mapping -g" \
        CFLAGS="-fprofile-instr-generate -fcoverage-mapping -g"

echo "make clean"
make -j$(nproc) clean
echo "make"
make -j$(nproc)
echo "make install"
make install

ls $WORK/lib
mv $WORK/lib/liblcms2.a $WORK/lib/liblcms2_profile.a

# Compile library for debugging
./configure --disable-shared --prefix="$WORK" \
        CXXFLAGS="-fsanitize=address -g -fPIE" \
        CFLAGS="-fsanitize=address -g -fPIE"

echo "make clean"
make -j$(nproc) clean
echo "make"
make -j$(nproc)
echo "make install"
make install

mv $WORK/lib/liblcms2.a $WORK/lib/liblcms2_cluster.a

# Compile library for fuzzing
./configure --disable-shared --prefix="$WORK" \
        CXXFLAGS="-fsanitize=fuzzer-no-link,address" \
        CFLAGS="-fsanitize=fuzzer-no-link,address"
        
echo "make clean"
make -j$(nproc) clean
echo "make"
make -j$(nproc)
echo "make install"
make install

echo "[INFO] Library installed in: $WORK"
