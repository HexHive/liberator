#!/bin/bash

##
# Pre-requirements:
# - env TARGET: path to target work dir
##

git clone --no-checkout https://github.com/vstakhov/libucl.git \
    "$TARGET/repo"
git -C "$TARGET/repo" checkout 5c58d0d5b939daf6f0c389e15019319f138636c2
