#!/bin/bash

# OLD_DRIVER=old_driver.txt

FOLDER=libdwarf

CNT=0
# while IFS= read -r odrv; do
for odrv in `ls $FOLDER/drivers_old`; do
    echo "$odrv -> driver$CNT.cc"
    mv "$FOLDER/drivers_old/$odrv" "$FOLDER/drivers/driver$CNT.cc"
    mkdir -p "$FOLDER/corpus/driver$CNT"
    head -c 400 </dev/urandom > "$FOLDER/corpus/driver$CNT/seed1.bin"
    CNT=$((CNT + 1))
done
# done < ${OLD_DRIVER}