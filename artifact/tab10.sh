#!/bin/bash

cd ../fuzzing_campaigns

export CONF=grammar_quick
source campaign_configuration.sh

GEN24_DEEP0=./gen24_deep0

./select_stable_drivers_cluster.py -d ${GEN24_DEEP0} -t 1 -simulate table 2> /dev/null

rm -f config.txt