#!/bin/bash
# This script is used to generate Figure 3 and Table 4 in the paper.

export CONF=grammar_quick 
source ../fuzzing_campaigns/campaign_configuration.sh

../tool/misc/plot_rq1.py -d ../fuzzing_campaigns/ -t 24h -i 3

rm config.txt
