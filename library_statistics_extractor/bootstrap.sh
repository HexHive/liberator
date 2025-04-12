#!/bin/bash
set -x
set -e

. ./env.sh
# cmake .
export PATH=$LLVM_DIR/bin:$PATH
export CXXFLAGS="-Wno-deprecated-declarations -Wfatal-errors"
# cmake -DCMAKE_BUILD_TYPE=Release .
cmake -DCMAKE_BUILD_TYPE=Debug  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON  .
