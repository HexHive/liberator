#!/bin/bash

set -e
set -x


cd ${TARGET}

SEED_DIR=./output_${ITER}/queue hopper cov output_${ITER}_cov


