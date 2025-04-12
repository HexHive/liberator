#!/bin/bash

set -e
set -x

# export LIBFUZZ=/workspaces/libfuzz/
# export TARGET=$LIBFUZZ/analysis/libtiff/ 

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
export LLVM_COMPILER_PATH=$LLVM_DIR/bin

# export CC=$LIBFUZZ/LLVM/build/bin/clang
# export CXX=$LIBFUZZ/LLVM/build/bin/clang++
export LIBFUZZ_LOG_PATH=$WORK/apipass
export CFLAGS=""


mkdir -p $LIBFUZZ_LOG_PATH

echo "make 1"
cd "$TARGET/repo"
echo "cmake"
cmake . -DCMAKE_INSTALL_PREFIX=$WORK -DBUILD_SHARED_LIBS=off \
        -DENABLE_STATIC=on -DCMAKE_BUILD_TYPE=Debug \
        -DCMAKE_C_FLAGS_DEBUG="-g -O0" \
        -DCMAKE_CXX_FLAGS_DEBUG="-g -O0" \
        -DBENCHMARK_ENABLE_GTEST_TESTS=off \
        -DBENCHMARK_ENABLE_INSTALL=off 

# configure compiles some shits for testing, better remove it
rm -rf $LIBFUZZ_LOG_PATH/apis.log

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

extract-bc -b $WORK/lib/libdwarf.a

# this extracts the exported functions in a file, to be used later for grammar
# generations
$TOOLS_DIR/tool/misc/extract_included_functions.py -i "$WORK/include" \
    -p "$LIBFUZZ/targets/${TARGET_NAME}/public_headers.txt" \
    -e "$LIBFUZZ_LOG_PATH/exported_functions.txt" \
    -t "$LIBFUZZ_LOG_PATH/incomplete_types.txt" \
    -a "$LIBFUZZ_LOG_PATH/apis_clang.json" \
    -n "$LIBFUZZ_LOG_PATH/enum_types.txt"

# extract fields dependency from the library itself, repeat for each object
# produced
$TOOLS_DIR/condition_extractor/bin/extractor \
    $WORK/lib/libdwarf.a.bc \
    -interface "$LIBFUZZ_LOG_PATH/apis_clang.json" \
    -output "$LIBFUZZ_LOG_PATH/conditions.json" \
    -minimize_api "$LIBFUZZ_LOG_PATH/apis_minimized.txt" \
    -v v0 -t json -do_indirect_jumps \
    -data_layout "$LIBFUZZ_LOG_PATH/data_layout.txt"

sed -i '/dwarf_register_printf_callback/d' "$LIBFUZZ_LOG_PATH/exported_functions.txt"
sed -i '/dwarf_register_printf_callback/d' "$LIBFUZZ_LOG_PATH/apis_minimized.txt"
sed -i '/dwarf_register_printf_callback/d' "$LIBFUZZ_LOG_PATH/apis_clang.json"
sed -i '/dwarf_register_printf_callback/d' "$LIBFUZZ_LOG_PATH/apis_llvm.json"
jq 'del(.[] | select(.function_name == "dwarf_register_printf_callback"))' "$LIBFUZZ_LOG_PATH/conditions.json" > temp.json && mv temp.json "$LIBFUZZ_LOG_PATH/conditions.json"
