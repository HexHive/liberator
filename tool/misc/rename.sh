#!/bin/bash

OLD_DRIVER=old_driver.txt

FOLDER=libpcap/drivers

CNT=0
# while IFS= read -r odrv; do
for odrv in `ls $FOLDER`; do
    echo "$odrv -> driver$CNT.cc"
    mv "$FOLDER/$odrv" "$FOLDER/driver$CNT.cc"
    mkdir -p "$FOLDER/corpus/driver$CNT"
    head -c 400 </dev/urandom > "$FOLDER/corpus/driver$CNT/seed1.bin"
    CNT=$((CNT + 1))
done
# done < ${OLD_DRIVER}