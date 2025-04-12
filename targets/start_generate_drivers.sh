#!/bin/bash


export TARGET_NAME=${TARGET}
export TARGET=${LIBFUZZ}/analysis/${TARGET}
# ENV TARGET_NAME ${target_name}

# echo "[TOOLS_DIR] ${TOOLS_DIR}"
echo "[TARGET] ${TARGET}"

${LIBFUZZ}/tool/main.py \
    --config ${LIBFUZZ}/targets/${TARGET_NAME}/generator.toml \
    --overwrite ${LIBFUZZ}/overwrite.toml
