#!/bin/bash
set -e
set -x

# NOTE: if TOOLD_DIR is unset, I assume to find stuffs in LIBFUZZ folder
if [ -z $TOOLS_DIR ]; then
    TOOLS_DIR=$LIBFUZZ
fi

WORK="$TARGET/work"
rm -rf "$WORK"
mkdir -p "$WORK"
mkdir -p "$WORK/lib" "$WORK/include"

export CC=wllvm
export CXX=wllvm++
export LLVM_COMPILER=clang
export LLVM_COMPILER_PATH=/usr/bin

export LIBFUZZ_LOG_PATH=$WORK/apipass

wllvm --version
mkdir -p $LIBFUZZ_LOG_PATH

echo "make 1"
cd "$TARGET/repo"
./autogen.sh --enable-debug --without-cython  --with-tools=no --without-tests --prefix="$WORK" \
                                CC=wllvm CXX=wllvm++ \
                                CXXFLAGS="-g -O0" \
                                CFLAGS="-g -O0"

echo "./configure"

# Compile library for coverage
#./configure --disable-shared --prefix="$WORK" \
#                                CC=wllvm CXX=wllvm++ \
#                                CXXFLAGS="-g -O0" \
#                                CFLAGS="-g -O0"

# WATCH OUT PADAWAN! SOMETIME SETTING -O0 IN C{XX}FLAGS MIGHT NOT BE ENOUGH!
find . -name Makefile -exec sed -i 's/-O2/-O0/g' {} \;

# configure compiles some shits for testing, better remove it
rm $LIBFUZZ_LOG_PATH/apis.log || true

touch $LIBFUZZ_LOG_PATH/exported_functions.txt
touch $LIBFUZZ_LOG_PATH/incomplete_types.txt
touch $LIBFUZZ_LOG_PATH/apis_clang.json
touch $LIBFUZZ_LOG_PATH/apis_llvm.json
touch $LIBFUZZ_LOG_PATH/coerce.log

echo "make clean"
make -j$(nproc) clean
echo "make"
make -j$(nproc)
echo "make install"
make install

extract-bc -b $WORK/lib/libplist-2.0.a

# this extracts the exported functions in a file, to be used later for grammar generations
$TOOLS_DIR/tool/misc/extract_included_functions.py -i "$WORK/include" \
    -p "$LIBFUZZ/targets/${TARGET_NAME}/public_headers.txt" \
    -e "$LIBFUZZ_LOG_PATH/exported_functions.txt" \
    -t "$LIBFUZZ_LOG_PATH/incomplete_types.txt" \
    -a "$LIBFUZZ_LOG_PATH/apis_clang.json" \
    -n "$LIBFUZZ_LOG_PATH/enum_types.txt"

# extract fields dependency from the library itself, repeat for each object produced
$TOOLS_DIR/condition_extractor/bin/extractor \
    $WORK/lib/libplist-2.0.a.bc \
    -interface "$LIBFUZZ_LOG_PATH/apis_clang.json" \
    -output "$LIBFUZZ_LOG_PATH/conditions.json" \
    -minimize_api "$LIBFUZZ_LOG_PATH/apis_minimized.txt" \
    -v v0 -t json -do_indirect_jumps \
    -data_layout "$LIBFUZZ_LOG_PATH/data_layout.txt"
