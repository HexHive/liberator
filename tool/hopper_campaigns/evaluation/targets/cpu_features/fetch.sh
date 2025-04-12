#!/bin/bash

##
# Pre-requirements:
# - env TARGET: path to target work dir
##

git clone --no-checkout https://android.googlesource.com/platform/external/cpu_features \
    "$TARGET/repo"
git -C "$TARGET/repo" checkout eca53ba6d2e951e174b64682eaf56a36b8204c89
