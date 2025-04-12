#!/bin/bash

set -e

# LLVMHome="llvm-13.0.0-custom.obj"

# cd "$HOME"

# copied from SVF/build.sh build_llvm_from_source
# mkdir "$LLVMHome"
echo "Downloading LLVM source..."
wget https://github.com/llvm/llvm-project/archive/refs/tags/llvmorg-14.0.0.zip -O llvm.zip
echo "Unzipping LLVM source..."
unzip llvm.zip &> /dev/null
mv llvm-project-llvmorg-14.0.0 llvm-project
rm llvm.zip