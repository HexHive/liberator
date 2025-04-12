#!/bin/bash

# make sure to be in the right folder
echo "[INFO] Moving to ${LIBFUZZ}"
cd ${LIBFUZZ}

# I need to install system clang
echo "[INFO] Install clang-12"
sudo ./update-alternatives-clang.sh 12 200

if [ ! -d llvm-project ]; then
    echo "[INFO] llvm-project not present, download it"
    # download LLVM 14
    ./install_llvm.sh
else
    echo "[INFO] llvm-project already here! I assume it is OK"
fi

cp custom-libfuzzer/build.sh llvm-project/

# compile my LLVM 14
echo "[INFO] compile LLVM"
./llvm-project/build.sh 