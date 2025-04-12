#!/bin/bash

set -e
set -x

cd ${TARGET}
./preinstall.sh
timeout ${TIMEOUT} hopper fuzz

