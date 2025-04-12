#!/bin/bash

source campaign_configuration.sh

for project in "${PROJECTS[@]}"; do
    export TARGET=$project
    ../docker/run_analysis.sh
done

echo "[INFO] Waiting for dockers to terminate..."
sleep 10s

for project in "${PROJECTS[@]}"; do
    docker wait libpp-analysis-$project
done

echo "[INFO] All analyses done!"
