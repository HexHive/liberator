#!/bin/bash

for l in `ls total_library_cluster`; do
        CLERR=./total_library_cluster/$l/clusters/
        # echo $CLERR
        if [ -d "$CLERR" ]; then
                SPURIOUS=`ls $CLERR | wc -l `
        else
                SPURIOUS=0
        fi
        echo $l"-"$SPURIOUS
done
