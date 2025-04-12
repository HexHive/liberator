#!/bin/bash

DOCKER_BUILDKIT=1 docker build --build-arg USER_UID=$(id -u) \
    --build-arg GROUP_UID=$(id -g) --target libfuzzpp_dev_image \
    -t libfuzzpp_dev_image -f ../Dockerfile ..
docker run -v $(pwd)/..:/workspaces/libfuzz libfuzzpp_dev_image /workspaces/libfuzz/bootstrap_llvm.sh
# docker run -it -v $(pwd)/..:/workspaces/libfuzz libfuzzpp_dev_image zsh