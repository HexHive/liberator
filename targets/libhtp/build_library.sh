#!/bin/bash
set -e

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

mv $WORK/lib/libhtp.a $WORK/lib/libhtp_profile.a
echo "make clean"
make -j$(nproc) clean

# Compile library for debugging
./configure --disable-shared --prefix="$WORK" \
        CXXFLAGS="-fsanitize=fuzzer-no-link,address -g" \
        CFLAGS="-fsanitize=fuzzer-no-link,address -g"

echo "make clean"
make -j$(nproc) clean
echo "make"
make -j$(nproc)
echo "make install"
make install

mv $WORK/lib/libhtp.a $WORK/lib/libhtp_cluster.a
echo "make clean"
make -j$(nproc) clean

# Compile library for fuzzing
./configure --disable-shared --prefix="$WORK" \
        CXXFLAGS="-fsanitize=fuzzer-no-link,address" \
        CFLAGS="-fsanitize=fuzzer-no-link,address" \
        --disable-debug 

echo "make"
make -j$(nproc)
echo "make install"
make install

echo "[INFO] Library installed in: $WORK"
