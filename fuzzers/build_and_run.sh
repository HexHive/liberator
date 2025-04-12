#!/bin/bash


if [ "$MODE" == "build" ] || [ "$MODE" == "build+run" ]; then
    ${TARGET}/build_driver.sh
fi

if [ "$MODE" == "run" ] || [ "$MODE" == "build+run" ]; then
    ${LIBPP_R}/fuzzers/run.sh
fi
