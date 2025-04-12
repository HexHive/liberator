#!/bin/bash -e

##
# Pre-requirements:
# - env TARGET: target name (from targets/)
##

if [ -z "$TARGET" ]; then
    echo "[ERROR] \$TARGET must be specified as an environment variable"
    exit 1
fi

IMG_NAME="libpp-analysis"
LIBPP=../

if [ -s "$LIBPP/analysis/$TARGET/work/apipass/conditions.json" ]; then
    echo "[INFO] Analysis for $TARGET already exists"
    exit 0
fi

set -x
DOCKER_BUILDKIT=1 docker build \
    --build-arg USER_UID=$(id -u) --build-arg GROUP_UID=$(id -g) \
    -t "$IMG_NAME" --target libfuzzpp_analysis \
    -f "$LIBPP/Dockerfile" "$LIBPP"
set +x

echo "$IMG_NAME"

if [[ "${DEVENV}" ]]; then
    docker run --env TARGET=${TARGET} -v "$(pwd)/..:/workspaces/libfuzz" \
        "$IMG_NAME"
else
    docker run --rm -d --name "${IMG_NAME}-${TARGET}" \
        --env TARGET=${TARGET} -v "$(pwd)/..:/workspaces/libfuzz" "$IMG_NAME"
fi
