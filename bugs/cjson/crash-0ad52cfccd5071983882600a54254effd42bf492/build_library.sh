#!/bin/bash

# repo commit 3249730

WORK="${HOME}/library/work"
rm -rf "$WORK"
mkdir -p "$WORK"
mkdir -p "$WORK/lib" "$WORK/include"

export LLVM_COMPILER_PATH=$LLVM_DIR/bin
export CC="$LLVM_COMPILER_PATH"/clang
export CXX="$LLVM_COMPILER_PATH"/clang++


cmake .. -DCMAKE_INSTALL_PREFIX="$WORK" -DBUILD_SHARED_AND_STATIC_LIBS=On \
        -DBUILD_SHARED_LIBS=off -DCMAKE_BUILD_TYPE=Debug \
        -DCMAKE_C_FLAGS_DEBUG="-fsanitize=address -gdwarf-4 -fPIE" \
        -DCMAKE_CXX_FLAGS_DEBUG="-fsanitize=address -gdwarf-4 -fPIE"


echo "make clean"
make -j"$(nproc)" clean
echo "make"
make -j"$(nproc)"
echo "make install"
make install
