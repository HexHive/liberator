#!/bin/bash

##
# Pre-requirements:
# - env TARGET: path to target work dir
##

git clone --no-checkout https://github.com/mm2/Little-CMS.git \
    "$TARGET/repo"
git -C "$TARGET/repo" checkout 2daf5c5859e1b62b6633ca755074e4de02459241
