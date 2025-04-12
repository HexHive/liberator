#!/bin/bash

if ! clang -v &> /dev/null
then
    echo "[INFO] clang not found, installing clang"
    sudo ${LIBFUZZ}/update-alternatives-clang.sh 12 200
fi

rm -Rf ${LIBFUZZ}/llvm-project/compiler-rt/lib/fuzzer
cp -r ${LIBFUZZ}/custom-libfuzzer/fuzzer ${LIBFUZZ}/llvm-project/compiler-rt/lib/fuzzer

pushd ${LIBFUZZ}/llvm-project
mkdir -p build

pushd build

if [ -z "$(ls -A .)" ]; then
   echo "[INFO] build folder is empty, re-run CMake"
   MODE=Release
   if [ $1 = "debug" ]; then
        MODE=Debug
   fi
   cmake -G Ninja -DLLVM_ENABLE_PROJECTS="clang;compiler-rt;lld" \
    -DLLVM_TARGETS_TO_BUILD=X86  -DCMAKE_BUILD_TYPE=${MODE} -DLLVM_OPTIMIZED_TABLEGEN=ON ../llvm/
fi

ninja clang compiler-rt llvm-symbolizer llvm-profdata llvm-cov \
    llvm-config llvm-dis opt lld
popd

popd