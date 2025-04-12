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

echo "make 1"
cd "$TARGET/repo"
echo "cmake"
mkdir "$TARGET/repo/pthreadpool_cov"
cd "$TARGET/repo/pthreadpool_cov"
# Compile library for coverage
cmake .. -DCMAKE_INSTALL_PREFIX=$WORK -DBUILD_SHARED_LIBS=off \
        -DENABLE_STATIC=on -DCMAKE_BUILD_TYPE=Debug \
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

mv $WORK/lib/libpthreadpool.a $WORK/lib/libpthreadpool_profile.a

cd ..
mkdir -p "$TARGET/repo/pthreadpool_cluster"
cd "$TARGET/repo/pthreadpool_cluster"

cmake .. -DCMAKE_INSTALL_PREFIX=$WORK -DBUILD_SHARED_LIBS=off \
        -DENABLE_STATIC=on -DCMAKE_BUILD_TYPE=Debug \
        -DCMAKE_C_FLAGS_DEBUG="-fsanitize=fuzzer-no-link,address -g" \
        -DCMAKE_CXX_FLAGS_DEBUG="-fsanitize=fuzzer-no-link,address -g" \
        -DBENCHMARK_ENABLE_GTEST_TESTS=off \
        -DBENCHMARK_ENABLE_INSTALL=off

find . -name "*.make" -exec sed -i 's/\-Werror//g' {} \;

echo "make clean"
make -j$(nproc) clean
echo "make"
make -j$(nproc)
echo "make install"
make install

mv $WORK/lib/libpthreadpool.a $WORK/lib/libpthreadpool_cluster.a

cd ..
mkdir -p "$TARGET/repo/pthreadpool_fuzz"
cd "$TARGET/repo/pthreadpool_fuzz"

cmake .. -DCMAKE_INSTALL_PREFIX=$WORK -DBUILD_SHARED_LIBS=off \
        -DENABLE_STATIC=on -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_C_FLAGS_RELEASE="-fsanitize=fuzzer-no-link,address" \
        -DCMAKE_CXX_FLAGS_RELEASE="-fsanitize=fuzzer-no-link,address" \
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
