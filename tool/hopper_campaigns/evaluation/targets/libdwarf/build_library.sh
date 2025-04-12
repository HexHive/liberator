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
export LIBFUZZ_LOG_PATH=$WORK/apipass

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

mkdir "$TARGET/repo/libdwarf_cov"
cd "$TARGET/repo/libdwarf_cov"

# Compile library for coverage

cmake .. -DCMAKE_INSTALL_PREFIX=$WORK_PROFILE -DBUILD_SHARED=YES \
	 -DBUILD_NON_SHARED=NO -DCMAKE_BUILD_TYPE=Debug \
	 -DCMAKE_C_FLAGS_DEBUG="-fprofile-instr-generate -fcoverage-mapping -g" \
	 -DCMAKE_CXX_FLAGS_DEBUG="-fprofile-instr-generate -fcoverage-mapping -g" \
	 -DBENCHMARK_ENABLE_GTEST_TESTS=off \
	 -DBENCHMARK_ENABLE_INSTALL=off


find . -name "*.make" -exec sed -i 's/\-Werror//g' {} \;

echo "make clean"
make -j$(nproc) clean
echo "make"
make -j$(nproc)
echo "make install"
make install


cd ..
mkdir -p "$TARGET/repo/libdwarf_fuzz"
cd "$TARGET/repo/libdwarf_fuzz"


cmake .. -DCMAKE_INSTALL_PREFIX=$WORK -DBUILD_SHARED=YES \
	 -DBUILD_NON_SHARED=NO -DCMAKE_BUILD_TYPE=Release \
	 -DBENCHMARK_ENABLE_GTEST_TESTS=off \
	 -DBENCHMARK_ENABLE_INSTALL=off


find . -name "*.make" -exec sed -i 's/\-Werror//g' {} \;

echo "make clean"
make -j$(nproc) clean
echo "make"
make -j$(nproc)
echo "make install"
make install


echo "[INFO] Library installed in: $WORK"
