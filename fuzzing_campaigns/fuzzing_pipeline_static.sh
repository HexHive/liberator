#!/bin/bash

export CONF=quickcamp; ./run_analysis.sh

export CONF=selection; ./run_generate_drivers.sh

export CONF=selection; ./run_fuzzing.sh; ./run_coverage.sh; ./get_total_library_coverage.sh; ./post_process.sh;

mkdir selection
mv results.csv selection
mv workdir_* selection
mv config.txt selection
mv total_library_coverage* selection

./select_stable_drivers.py -report selection/results.csv -rootdir selection -threshold 0.6 -timebudget 24h

export CONF=long; ./run_fuzzing.sh; ./run_coverage.sh; ./get_total_library_coverage.sh; ./post_process.sh;