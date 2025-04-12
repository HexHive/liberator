#!/bin/bash

../tool/misc/calc_api_over_time.py -r ../fuzzing_campaigns/gen24_deep0/workdir_X_X -p

mkdir -p api_coverage
mv *.pdf api_coverage
