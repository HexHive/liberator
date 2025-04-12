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

WORK="$TARGET/work"
rm -rf "$WORK"
mkdir -p "$WORK"
mkdir -p "$WORK/lib" "$WORK/include"

export LIBFUZZ_LOG_PATH=$WORK/apipass

echo "make 1"
echo "make 1"
mkdir -p "$TARGET/repo/cpu_features_build_cov"
cd "$TARGET/repo/cpu_features_build_cov"
# cd "$TARGET/repo"

# Compile library for coverage
cmake .. -DCMAKE_INSTALL_PREFIX=$WORK -DBUILD_SHARED_LIBS=off \
        -DENABLE_STATIC=on -DCMAKE_BUILD_TYPE=Debug \
        -DCMAKE_C_FLAGS_DEBUG="-fprofile-instr-generate -fcoverage-mapping -g" \
        -DCMAKE_CXX_FLAGS_DEBUG="-fprofile-instr-generate -fcoverage-mapping -g"

echo "make clean"
make -j$(nproc) clean
echo "make"
make -j$(nproc)
echo "make install"
make install

mv $WORK/lib/libcpu_features.a $WORK/lib/libcpu_features_profile.a

cd ..
mkdir -p "$TARGET/repo/cpu_features_build_cluster"
cd "$TARGET/repo/cpu_features_build_cluster"

# Compile library for clustering
cmake .. -DCMAKE_INSTALL_PREFIX=$WORK -DBUILD_SHARED_LIBS=off \
        -DENABLE_STATIC=on -DCMAKE_BUILD_TYPE=DEBUG \
        -DCMAKE_C_FLAGS_DEBUG="-fsanitize=fuzzer-no-link,address -g" \
        -DCMAKE_CXX_FLAGS_DEBUG="-fsanitize=fuzzer-no-link,address -g"

echo "make clean"
make -j$(nproc) clean
echo "make"
make -j$(nproc)
echo "make install"
make install

mv $WORK/lib/libcpu_features.a $WORK/lib/libcpu_features_cluster.a

cd ..
mkdir -p "$TARGET/repo/cpu_features_build_fuzz"
cd "$TARGET/repo/cpu_features_build_fuzz"

# Compile library for fuzzing
cmake .. -DCMAKE_INSTALL_PREFIX=$WORK -DBUILD_SHARED_LIBS=off \
        -DENABLE_STATIC=on -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_C_FLAGS_RELEASE="-fsanitize=fuzzer-no-link,address" \
        -DCMAKE_CXX_FLAGS_RELEASE="-fsanitize=fuzzer-no-link,address"

echo "make clean"
make -j$(nproc) clean
echo "make"
make -j$(nproc)
echo "make install"
make install

echo "[INFO] Library installed in: $WORK"
