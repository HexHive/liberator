#!/bin/bash

##
# Pre-requirements:
# - env TARGET: path to target work dir
##

git clone --no-checkout https://github.com/libimobiledevice/libplist.git \
    "$TARGET/repo"
git -C "$TARGET/repo" checkout 44099d4b79c8d6a7d599d652ebef62db8dae6696
