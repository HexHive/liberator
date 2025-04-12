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
./configure --disable-shared --prefix="$WORK" \
        CXXFLAGS="-fsanitize=fuzzer-no-link -g" \
        CFLAGS="-fsanitize=fuzzer-no-link -g"
        
echo "make clean"
make -j$(nproc) clean
echo "make"
make -j$(nproc)
echo "make install"
make install

echo "[INFO] Library installed in: $WORK"