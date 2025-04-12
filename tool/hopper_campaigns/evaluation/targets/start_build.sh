#!/bin/bash
set -e
set -x

export TARGET_NAME=${TARGET}
export TARGET=$(pwd)/${TARGET}
# ENV TARGET_NAME ${target_name}


cd ${TARGET_NAME}
./preinstall.sh
./fetch.sh
./build_library.sh
#hopper compile
#./compile_profile.sh

