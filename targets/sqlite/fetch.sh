#!/bin/bash

##
# Pre-requirements:
# - env TARGET: path to target work dir
##

git clone --no-checkout https://github.com/sqlite/sqlite.git \
    "$TARGET/repo"
git -C "$TARGET/repo" checkout 538ad6ce58c47e48f2c85abfcb31c968e615fc40
