#!/bin/bash

echo "[INFO] Unzipping analysis_result.zip"

if [ -d "analysis" ]; then
  echo "[INFO] 'analysis' folder exists! Nothing to do."
  exit 0
fi

wget https://zenodo.org/records/15174089/files/analysis_result.zip

unzip analysis_result.zip 
rm -drf analysis_result.zip 
