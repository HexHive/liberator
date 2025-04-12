#!/bin/bash -e

##
# Pre-requirements:
# - env TARGET: target name (from targets/)
##

if [ -z $TARGET ]; then
    echo '$TARGET must be specified as environment variable.'
    exit 1
fi


IMG_NAME="libpp-coverage-$TARGET"
LIBPP=../

set -x
DOCKER_BUILDKIT=1 docker build \
    --build-arg USER_UID=$(id -u) --build-arg GROUP_UID=$(id -g) \
    --build-arg target_name="$TARGET" \
    -t "$IMG_NAME" --target libfuzzpp_coverage \
    -f "$LIBPP/Dockerfile" "$LIBPP"
set +x

echo "[INFO] Running: $IMG_NAME"

docker run --env DRIVER=${DRIVER} --env TIMEOUT=${TIMEOUT} \
    -v $(pwd)/..:/workspaces/libfuzz $IMG_NAME
