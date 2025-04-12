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
./autogen.sh --without-cython
echo "./configure"

# Compile library for coverage
./configure --without-cython  --prefix="$WORK" --with-tools=no --without-tests --enable-debug \
        CXXFLAGS="-fprofile-instr-generate -fcoverage-mapping -g" \
        CFLAGS="-fprofile-instr-generate -fcoverage-mapping -g"

echo "make clean"
make -j$(nproc) clean
echo "make"
make -j$(nproc)
echo "make install"
make install

mv $WORK/lib/libplist-2.0.a $WORK/lib/libplist-2.0_profile.a
echo "make clean"
make -j$(nproc) clean

# Compile library for debugging
./configure --without-cython  --prefix="$WORK" --with-tools=no --without-tests --enable-debug  \
        CXXFLAGS="-fsanitize=fuzzer-no-link,address -g" \
        CFLAGS="-fsanitize=fuzzer-no-link,address -g"

echo "make clean"
make -j$(nproc) clean
echo "make"
make -j$(nproc)
echo "make install"
make install

mv $WORK/lib/libplist-2.0.a $WORK/lib/libplist-2.0_cluster.a
echo "make clean"
make -j$(nproc) clean

# Compile library for fuzzing
./configure --without-cython --without-tests --with-tools=no --prefix="$WORK" \
        CXXFLAGS="-fsanitize=fuzzer-no-link,address" \
        CFLAGS="-fsanitize=fuzzer-no-link,address" \
        --disable-debug 

echo "make"
make -j$(nproc)
echo "make install"
make install

echo "[INFO] Library installed in: $WORK"
