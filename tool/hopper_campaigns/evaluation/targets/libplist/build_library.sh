#!/bin/bash
set -e


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

WORK_PROFILE="$TARGET/work_profile"
rm -rf "$WORK_PROFILE"
mkdir -p "$WORK_PROFILE"
mkdir -p "$WORK_PROFILE/lib" "$WORK_PROFILE/include"

echo "make 1"
cd "$TARGET/repo"
./autogen.sh --without-cython
echo "./configure"

# Compile library for coverage
./configure --without-cython  --prefix="$WORK_PROFILE" --with-tools=no --without-tests --enable-debug \
        CXXFLAGS="-fprofile-instr-generate -fcoverage-mapping -g" \
        CFLAGS="-fprofile-instr-generate -fcoverage-mapping -g"

echo "make clean"
make -j$(nproc) clean
echo "make"
make -j$(nproc)
echo "make install"
make install



# Compile library for fuzzing
./configure --without-cython --without-tests --with-tools=no --prefix="$WORK" \
        --disable-debug 

echo "make"
make -j$(nproc)
echo "make install"
make install

echo "[INFO] Library installed in: $WORK"
