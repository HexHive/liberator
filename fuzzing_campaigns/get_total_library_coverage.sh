#!/bin/bash -e

source campaign_configuration.sh

IMG_NAME="libpp-coverage"
LIBPP=../

echo "[INFO] Running: $IMG_NAME"


for project in "${PROJECTS[@]}"; do
    set -x
    DOCKER_BUILDKIT=1 docker build \
        --build-arg USER_UID=$(id -u) --build-arg GROUP_UID=$(id -g) \
        --build-arg target_name="$project" \
        -t "${IMG_NAME}-${project}" --target libfuzzpp_coverage \
        -f "$LIBPP/Dockerfile" "$LIBPP"
    set +x
done

rm total_library_coverage.csv || true
touch total_library_coverage.csv

rm total_library_coverage_per_iter.csv || true
touch total_library_coverage_per_iter.csv

for project in "${PROJECTS[@]}"; do
    docker run --env TOTAL_LIBRARY_COVERAGE="YES" \
               --env ITERATIONS=${ITERATIONS} \
               --env GRAMMAR_MODE=${GRAMMAR_MODE} \
               -v $(pwd)/..:/workspaces/libfuzz "${IMG_NAME}-${project}"
    LIBRARY_COVERAGE_REPORT="./total_library_coverage/${project}/report"
    total_coverage=$(tail -n 1 $LIBRARY_COVERAGE_REPORT | awk '{print $13}')
    echo "${project},${total_coverage}" >> total_library_coverage.csv

    for i in $( eval echo {1..$ITERATIONS} ); do
        ITER_COVERAGE_REPORT="./total_library_coverage/${project}/iter_${i}/report"
        iter_coverage=$(tail -n 1 $ITER_COVERAGE_REPORT | awk '{print $13}')
        echo "${project},${i},${iter_coverage}" >> total_library_coverage_per_iter.csv
    done
done
