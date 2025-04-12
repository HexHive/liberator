#!/bin/bash

CXX=$LLVM_DIR/bin/clang++

$CXX -std=c++11 -I/tmp/uriparser_vanilla/work/include main.cc /tmp/uriparser_vanilla/work/lib/liburiparser.a -o main