#!/bin/bash

TARGET_DIR="/home/nbadoux/libfuzz/oss-llm-targets"
DOWNLOAD_DIR="/home/nbadoux/oss-fuzz-llm-targets-public/"  # Update this path to where the files are downloaded

mkdir -p "$TARGET_DIR"

declare -A driver_counts

# Find all C library directories
for lib_dir in "$DOWNLOAD_DIR"/*; do
    if [ -d "$lib_dir" ]; then
        lib_name=$(basename "$lib_dir" | cut -d'-' -f1)
        driver_count=${driver_counts[$lib_name]:-1}
        driver_found=false

        for driver in "$lib_dir/targets"/*.{c,cc}; do
            if [ -f "$driver" ]; then
                if [ "$driver_found" = false ]; then
                    mkdir -p "$TARGET_DIR/$lib_name/drivers"
                    mkdir -p "$TARGET_DIR/$lib_name/corpus"
                    driver_found=true
                fi

                driver_name="driver${driver_count}.cc"
                cp "$driver" "$TARGET_DIR/$lib_name/drivers/$driver_name"

                # Create seed file with random content
                seed_dir="$TARGET_DIR/$lib_name/corpus/driver${driver_count}"
               
                mkdir -p "$seed_dir" 
                if [ ! -f "$seed_dir"/seed ]; then
                    head -c 200k </dev/urandom >"$seed_dir/seed"
                fi

                driver_count=$((driver_count + 1))
            fi
        done

        driver_counts[$lib_name]=$driver_count
    fi
done
