#!/bin/bash

##
# Pre-requirements:
# - env TARGET: path to target work dir
##

git clone --no-checkout https://github.com/uriparser/uriparser.git \
    "$TARGET/repo"
git -C "$TARGET/repo" checkout 1762d5ff025fb07b4b8ccd1a8a9635009b2e9e34