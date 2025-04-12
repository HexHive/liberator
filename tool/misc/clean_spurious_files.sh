#!/bin/bash

find -maxdepth 1 -type f -regextype posix-basic -regex '^.*/[^/]*[[:cntrl:]][^/]*$' -exec rm {} \;
find . -maxdepth 1 -name "<fd*" -exec rm {} \;
rm -f *.bin
rm -f core.*
# Remove files that do not have alphanumeric characters, dots, underscores, or hyphens
find . -maxdepth 1 -type f ! -name '[a-zA-Z0-9._\- ()]*' -exec rm {} \;

echo "[INFO] NOTE: If you have better way to remove temporary files feel free to update $0"
