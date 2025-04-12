#!/bin/bash

# docker build -t vsc-libfuzz-230af0437939dbfc00081fc163ef918b -f Dockerfile . 
# docker run -it -v "$(pwd):/workspaces/libfuzz" vsc-libfuzz-230af0437939dbfc00081fc163ef918b zsh

DOCKER_BUILDKIT=1 docker build --build-arg USER_UID=$(id -u) \
    --build-arg GROUP_UID=$(id -g) --target libfuzzpp_dev_image \
    -t libfuzzpp_dev_image -f Dockerfile . 
docker run -it -v $(pwd):/workspaces/libfuzz libfuzzpp_dev_image zsh
