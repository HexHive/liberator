#!/bin/sh

echo "[INFO] This script is to be run *on the host* before any other experiment"

# pip3 install -r requirements_host.txt

REQ_FILE="requirements_host.txt"

while IFS= read -r line; do
    # Skip comments and empty lines
    # [[ "$line" =~ ^#.*$ || -z "$line" ]] && continue
    if [ -z "$line" ]; then
        continue
    fi

    # Extract package name (remove version if any)
    pkg_name=$(echo "$line" | cut -d '=' -f 1 | cut -d '<' -f 1 | cut -d '>' -f 1 | tr -d ' ')

    echo "Trying to install $pkg_name via pip..."
    if ! pip3 install "$line"; then
        echo "pip install failed for $pkg_name, trying apt..."
        pkg_name_lower=$(echo "$pkg_name" | tr '[:upper:]' '[:lower:]')
        sudo apt-get update
        sudo apt-get install -y "python3-$pkg_name_lower"
    fi
done < "$REQ_FILE"

# cd docker
# ./build_llvm.sh
# cd -
