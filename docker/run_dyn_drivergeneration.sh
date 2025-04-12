#!/bin/bash

if [ -z ${TARGET} ]; then
    echo '$TARGET must be specified as environment variables.'
    exit 1
fi

if [ -z ${TIMEOUT} ]; then
    TIMEOUT=12h
fi

if [ -z ${HOST_PORT} ]; then
    HOST_PORT=5000
fi

if [ -z ${POLICY} ]; then
    POLICY="constraint_based_grammar"
fi

PARALLEL_OPTS=""
if [ $CPU_ID ]; then
    PARALLEL_OPTS="${PARALLEL_OPTS} --cpuset-cpus ${CPU_ID} -d "
fi

if [ $CONTAINER_NAME ]; then
    PARALLEL_OPTS="${PARALLEL_OPTS} --name ${CONTAINER_NAME} "
fi

DRIVER_TIMEOUT=5m

IMG_NAME="libpp-dyndrvgen-${TARGET}"
LIBPP=../

set -x
DOCKER_BUILDKIT=1 docker build \
    --build-arg USER_UID=$(id -u) --build-arg GROUP_UID=$(id -g) \
    --build-arg target_name="${TARGET}" \
    -t "$IMG_NAME" --target libfuzzpp_dyndrvgen \
    -f "${LIBPP}/Dockerfile" "${LIBPP}"
set +x

echo "[INFO] Running: $IMG_NAME"
docker run ${PARALLEL_OPTS} -p ${HOST_PORT}:5000 --rm --env DRIVER=${DRIVER} \
    --env WHOLE_TIMEOUT=${TIMEOUT} --env RESULTS_FOLDER=${RESULTS_FOLDER} \
    --env TIMEOUT=${DRIVER_TIMEOUT} --env POLICY=${POLICY} \
    --mount type=tmpfs,destination=/tmpfs \
    -v $(pwd)/..:/workspaces/libfuzz $IMG_NAME
