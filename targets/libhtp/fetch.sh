#!/bin/bash

##
# Pre-requirements:
# - env TARGET: path to target work dir
##

git clone --no-checkout https://github.com/OISF/libhtp.git \
    "$TARGET/repo"
git -C "$TARGET/repo" checkout 202be0f21622352fc3955efaa4112b2fec304dc7