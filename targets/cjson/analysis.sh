#!/bin/bash

set -e
set -x

# NOTE: if TOOLD_DIR is unset, I assume to find stuffs in LIBFUZZ folder
if [ -z "$TOOLS_DIR" ]; then
    TOOLS_DIR=$LIBFUZZ
fi

WORK="$TARGET/work"
rm -rf "$WORK"
mkdir -p "$WORK"
mkdir -p "$WORK/lib" "$WORK/include"

export CC=wllvm
export CXX=wllvm++
export LLVM_COMPILER=clang
echo "$LLVM_DIR"
export LLVM_COMPILER_PATH=$LLVM_DIR/bin

# export CC=$LIBFUZZ/LLVM/build/bin/clang
# export CXX=$LIBFUZZ/LLVM/build/bin/clang++
export LIBFUZZ_LOG_PATH=$WORK/apipass
# export CFLAGS="-mllvm -get-api-pass"


mkdir -p "$LIBFUZZ_LOG_PATH"

echo "make 1"
mkdir -p "$TARGET/repo/cJSON_build"
cd "$TARGET/repo/cJSON_build"


cmake .. -DCMAKE_INSTALL_PREFIX="$WORK" -DBUILD_SHARED_AND_STATIC_LIBS=On \
        -DBUILD_SHARED_LIBS=off -DCMAKE_BUILD_TYPE=Debug \
        -DCMAKE_C_FLAGS_DEBUG="-g -O0" \
        -DCMAKE_CXX_FLAGS_DEBUG="-g -O0"
# configure compiles some shits for testing, better remove it
rm -rf "$LIBFUZZ_LOG_PATH"/apis.log

touch "$LIBFUZZ_LOG_PATH"/exported_functions.txt
touch "$LIBFUZZ_LOG_PATH"/incomplete_types.txt
touch "$LIBFUZZ_LOG_PATH"/apis_clang.json
touch "$LIBFUZZ_LOG_PATH"/apis_llvm.json
touch "$LIBFUZZ_LOG_PATH"/coerce.log

echo "make clean"
make -j"$(nproc)" clean
echo "make"
make -j"$(nproc)"
echo "make install"
make install

extract-bc -b "$WORK"/lib/libcjson.a

# this extracts the exported functions in a file, to be used later for grammar
# generations
"$TOOLS_DIR"/tool/misc/extract_included_functions.py -i "$WORK/include" \
    -p "$LIBFUZZ/targets/${TARGET_NAME}/public_headers.txt" \
    -e "$LIBFUZZ_LOG_PATH/exported_functions.txt" \
    -t "$LIBFUZZ_LOG_PATH/incomplete_types.txt" \
    -a "$LIBFUZZ_LOG_PATH/apis_clang.json" \
    -n "$LIBFUZZ_LOG_PATH/enum_types.txt"

# extract fields dependency from the library itself, repeat for each object
# produced
"$TOOLS_DIR"/condition_extractor/bin/extractor \
    "$WORK"/lib/libcjson.a.bc \
    -interface "$LIBFUZZ_LOG_PATH/apis_clang.json" \
    -output "$LIBFUZZ_LOG_PATH/conditions.json" \
    -minimize_api "$LIBFUZZ_LOG_PATH/apis_minimized.txt" \
    -v v0 -t json -do_indirect_jumps \
    -data_layout "$LIBFUZZ_LOG_PATH/data_layout.txt"

# manual way to modify automatically extracted constraints
# TMP_FILE=/tmp/const.tmp

# NEW_FIELD_CONSTRAINT=$(cat <<EOF
# {
#     "access": "create",
#     "fields": [],
#     "parent": 0,
#     "type": "13e78f7269fb4001160f783455a4ca4d",
#     "type_string": "%struct.cJSON*"
# }
# EOF
# )
# echo ${NEW_FIELD_CONSTRAINT} > ${TMP_FILE}

# APIS="cJSON_CreateBool cJSON_AddNumberToObject cJSON_ParseWithOpts cJSON_CreateStringArray cJSON_CreateObjectReference cJSON_AddStringToObject cJSON_CreateArray cJSON_CreateTrue cJSON_AddTrueToObject cJSON_AddNullToObject  cJSON_CreateRaw cJSON_AddObjectToObject cJSON_Parse cJSON_AddBoolToObject cJSON_ParseWithLengthOpts cJSON_CreateString cJSON_CreateFalse cJSON_ParseWithLength cJSON_CreateNumber cJSON_AddArrayToObject cJSON_CreateArrayReference cJSON_CreateIntArray cJSON_CreateObject cJSON_CreateDoubleArray cJSON_AddFalseToObject cJSON_Duplicate cJSON_AddRawToObject cJSON_CreateStringReference cJSON_CreateNull cJSON_CreateFloatArray"

# for a in ${APIS}; do
#     $LIBFUZZ/tool/misc/edit_constraints.py -n ${TMP_FILE} \
#                     -f ${a} -a -1 \
#                     -c "$LIBFUZZ_LOG_PATH/conditions.json"
# done

# rm -f ${TMP_FILE}
