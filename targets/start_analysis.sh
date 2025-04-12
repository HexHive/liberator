#!/bin/bash
set -e
set -x

export TARGET_NAME=${TARGET}
export TARGET=${LIBFUZZ}/analysis/${TARGET}
# ENV TARGET_NAME ${target_name}

echo "[TOOLS_DIR] ${TOOLS_DIR}"
echo "[TARGET] ${TARGET}"
echo "[WLLVM] `which wllvm`"

cd ${LIBFUZZ}/targets/${TARGET_NAME}
sudo ./preinstall.sh
./fetch.sh
{ time ./analysis.sh ; } 2> ${LIBFUZZ}/${TARGET_NAME}_analysis_time.txt