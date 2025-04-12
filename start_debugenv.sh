#!/bin/bash

# docker build -t vsc-libfuzz-230af0437939dbfc00081fc163ef918b -f Dockerfile . 
# docker run -it -v "$(pwd):/workspaces/libfuzz" vsc-libfuzz-230af0437939dbfc00081fc163ef918b zsh


if [ $# -ne 1 ]; then
    echo "[ERROR] Specify which target you want to debug: $0 TARGET_NAME"
    exit 1
fi
TARGET=$1
echo "Debugging target ${TARGET}"

DOCKER_IMAGE=libfuzzpp_debug_${TARGET}

DOCKER_BUILDKIT=1 docker build --build-arg USER_UID=$(id -u) \
     --build-arg GROUP_UID=$(id -g) --target libfuzzpp_debug \
     --build-arg target_name="${TARGET}" \
     -t ${DOCKER_IMAGE} -f Dockerfile . 
docker run -it -v $(pwd):/workspaces/libfuzz ${DOCKER_IMAGE} zsh
