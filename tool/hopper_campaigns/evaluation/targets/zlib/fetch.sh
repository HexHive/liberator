#!/bin/bash

##
# Pre-requirements:
# - env TARGET: path to target work dir
##

git clone --no-checkout https://github.com/madler/zlib  \
    "$TARGET/repo"
git -C "$TARGET/repo" checkout 0f51fb4933fc9ce18199cb2554dacea8033e7fd3
