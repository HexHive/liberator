#!/bin/bash

set -e

##
# Pre-requirements:
# - env TARGET: path to target work dir
# - env OUT: path to directory where artifacts are stored
# - env CC, CXX, FLAGS, LIBS, etc...
##

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

build_dir="$TARGET/build"

# Build libvpx for coverage
rm -rf ${build_dir}
mkdir -p ${build_dir}
pushd ${build_dir}

export CXXFLAGS="-fprofile-instr-generate -fcoverage-mapping -g"
export CFLAGS="-fprofile-instr-generate -fcoverage-mapping -g"

# oss-fuzz has 2 GB total memory allocation limit. So, we limit per-allocation
# limit in libvpx to 1 GB to avoid OOM errors. A smaller per-allocation is
# needed for MemorySanitizer (see bug oss-fuzz:9497 and bug oss-fuzz:9499).
if [[ $CFLAGS = *sanitize=memory* ]]; then
  extra_c_flags='-DVPX_MAX_ALLOCABLE_MEMORY=536870912'
else
  extra_c_flags='-DVPX_MAX_ALLOCABLE_MEMORY=1073741824'
fi

LDFLAGS="$CXXFLAGS" LD=$CXX $TARGET/repo/configure \
    --prefix="$WORK" \
    --enable-vp9-highbitdepth \
    --disable-unit-tests \
    --disable-examples \
    --size-limit=12288x12288 \
    --extra-cflags="${extra_c_flags}" \
    --disable-webm-io \
    --enable-debug 
make -j all
make install
popd

mv $WORK/lib/libvpx.a $WORK/lib/libvpx_profile.a

# Build libvpx for clustering
rm -rf ${build_dir}
mkdir -p ${build_dir}
pushd ${build_dir}

export CXXFLAGS="-fsanitize=fuzzer-no-link,address -g"
export CFLAGS="-fsanitize=fuzzer-no-link,address -g"

# oss-fuzz has 2 GB total memory allocation limit. So, we limit per-allocation
# limit in libvpx to 1 GB to avoid OOM errors. A smaller per-allocation is
# needed for MemorySanitizer (see bug oss-fuzz:9497 and bug oss-fuzz:9499).
if [[ $CFLAGS = *sanitize=memory* ]]; then
  extra_c_flags='-DVPX_MAX_ALLOCABLE_MEMORY=536870912'
else
  extra_c_flags='-DVPX_MAX_ALLOCABLE_MEMORY=1073741824'
fi

LDFLAGS="$CXXFLAGS" LD=$CXX $TARGET/repo/configure \
    --prefix="$WORK" \
    --enable-vp9-highbitdepth \
    --disable-unit-tests \
    --disable-examples \
    --size-limit=12288x12288 \
    --extra-cflags="${extra_c_flags}" \
    --disable-webm-io \
    --enable-debug 
make clean
make -j all
make install
popd

mv $WORK/lib/libvpx.a $WORK/lib/libvpx_cluster.a

# Build libvpx for fuzzing
rm -rf ${build_dir}
mkdir -p ${build_dir}
pushd ${build_dir}

export CXXFLAGS="-fsanitize=fuzzer-no-link,address"
export CFLAGS="-fsanitize=fuzzer-no-link,address"

# oss-fuzz has 2 GB total memory allocation limit. So, we limit per-allocation
# limit in libvpx to 1 GB to avoid OOM errors. A smaller per-allocation is
# needed for MemorySanitizer (see bug oss-fuzz:9497 and bug oss-fuzz:9499).
if [[ $CFLAGS = *sanitize=memory* ]]; then
  extra_c_flags='-DVPX_MAX_ALLOCABLE_MEMORY=536870912'
else
  extra_c_flags='-DVPX_MAX_ALLOCABLE_MEMORY=1073741824'
fi

LDFLAGS="$CXXFLAGS" LD=$CXX $TARGET/repo/configure \
    --prefix="$WORK" \
    --enable-vp9-highbitdepth \
    --disable-unit-tests \
    --disable-examples \
    --size-limit=12288x12288 \
    --extra-cflags="${extra_c_flags}" \
    --disable-webm-io \
    --disable-debug 
make clean
make -j all
make install
popd

echo "[INFO] Library installed in: $WORK"
