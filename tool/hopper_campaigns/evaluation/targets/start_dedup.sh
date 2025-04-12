#!/bin/bash

set -e
set -x

cd ${TARGET}

mv output_${ITER} output
cd output
if ! ./bin/hopper-sanitizer; then 
    echo "hopper-sanitizer failed, but continuing..."
fi
cd ..
mv output output_${ITER}


