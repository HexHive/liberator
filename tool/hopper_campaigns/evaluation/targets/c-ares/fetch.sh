#!/bin/bash

##
# Pre-requirements:
# - env TARGET: path to target work dir
##
git clone --no-checkout https://github.com/c-ares/c-ares.git \
    "$TARGET/repo"
git -C "$TARGET/repo" checkout 25ad4ca231054ba210ea5a31a5a15195d03e70b6

