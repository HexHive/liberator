#!/bin/bash


./bin/extractor /workspaces/libfuzz/analysis/cpu_features/work/lib/libcpu_features.a.bc \
    -interface /workspaces/libfuzz/analysis/cpu_features/work/apipass/apis_clang.json \
    -do_indirect_jumps -v v0 -t json \
    -output /workspaces/libfuzz/analysis/cpu_features/work/apipass/weights.json

./bin/extractor /workspaces/libfuzz/analysis/libtiff/work/lib/libtiff.a.bc \
    -interface /workspaces/libfuzz/analysis/libtiff/work/apipass/apis_clang.json \
    -do_indirect_jumps -v v0 -t json \
    -output /workspaces/libfuzz/analysis/libtiff/work/apipass/weights.json

./bin/extractor /workspaces/libfuzz/analysis/minijail/work/lib/libminijail.pie.a.bc \
    -interface /workspaces/libfuzz/analysis/minijail/work/apipass/apis_clang.json \
    -do_indirect_jumps -v v0 -t json \
    -output /workspaces/libfuzz/analysis/minijail/work/apipass/weights.json

./bin/extractor /workspaces/libfuzz/analysis/pthreadpool/work/lib/libpthreadpool.a.bc \
    -interface /workspaces/libfuzz/analysis/pthreadpool/work/apipass/apis_clang.json \
    -do_indirect_jumps -v v0 -t json \
    -output /workspaces/libfuzz/analysis/pthreadpool/work/apipass/weights.json

./bin/extractor /workspaces/libfuzz/analysis/libaom/work/lib/libaom.a.bc \
    -interface /workspaces/libfuzz/analysis/libaom/work/apipass/apis_clang.json \
    -do_indirect_jumps -v v0 -t json \
    -output /workspaces/libfuzz/analysis/libaom/work/apipass/weights.json

./bin/extractor /workspaces/libfuzz/analysis/libvpx/work/lib/libvpx.a.bc \
    -interface /workspaces/libfuzz/analysis/libvpx/work/apipass/apis_clang.json \
    -do_indirect_jumps -v v0 -t json \
    -output /workspaces/libfuzz/analysis/libvpx/work/apipass/weights.json

./bin/extractor /workspaces/libfuzz/analysis/libhtp/work/lib/libhtp.a.bc \
    -interface /workspaces/libfuzz/analysis/libhtp/work/apipass/apis_clang.json \
    -do_indirect_jumps -v v0 -t json \
    -output /workspaces/libfuzz/analysis/libhtp/work/apipass/weights.json

./bin/extractor /workspaces/libfuzz/analysis/libpcap/work/lib/libpcap.a.bc \
    -interface /workspaces/libfuzz/analysis/libpcap/work/apipass/apis_clang.json \
    -do_indirect_jumps -v v0 -t json \
    -output /workspaces/libfuzz/analysis/libpcap/work/apipass/weights.json


./bin/extractor /workspaces/libfuzz/analysis/c-ares/work/lib/libcares_static.a.bc \
    -interface /workspaces/libfuzz/analysis/c-ares/work/apipass/apis_clang.json \
    -do_indirect_jumps -v v0 -t json \
    -output /workspaces/libfuzz/analysis/c-ares/work/apipass/weights.json