#!/bin/bash

export CONF=ossllm;
source campaign_configuration.sh

rm -drf workdir_XX_X
cp `pwd`/../oss-llm-targets workdir_XX_X -r

echo $TIMEOUT

# Extract the numeric part and the unit
number=${TIMEOUT%[a-zA-Z]*}
unit=${TIMEOUT##*[0-9]}

# Convert based on the unit
case "$unit" in
  h) seconds=$((number * 3600)) ;;
  m) seconds=$((number * 60)) ;;
  s) seconds=$((number)) ;;
  *) echo "Unknown unit"; exit 1 ;;
esac

rm time_budget.csv || true
# touch time_budget.csv
for project in "${PROJECTS[@]}"; do
    N_DRIVER="$(ls ./workdir_XX_X/${project}/drivers/driver*.cc | wc -l)"
    time_slot=$((seconds / N_DRIVER))
    echo "${project}|${time_slot}" >> time_budget.csv
done

./run_rebuild_drivers.sh; ./run_fuzzing.sh; ./run_coverage.sh; ./get_total_library_coverage.sh; ./post_process.sh;
