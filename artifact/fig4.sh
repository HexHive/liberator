#!/bin/bash

export CONF=grammar_quick 
source ../fuzzing_campaigns/campaign_configuration.sh

# echo ${PROJECTS_STRING}

for project in "${PROJECTS[@]}"; do
    # set -x
    echo $project
    ../tool/misc/plot_cumulative_coverage.py -working_dir \
        ../fuzzing_campaigns/gen24_deep0/workdir_X_X -target $project \
        -is_grammar
    # set +x
done

rm config.txt

mkdir -p comulative_coverage
mv *.pdf comulative_coverage
