#!/bin/bash

##
# Pre-requirements:
# - env TARGET: path to target work dir
##
git clone --no-checkout https://aomedia.googlesource.com/aom \
    "$TARGET/repo"
git -C "$TARGET/repo" checkout a0f61021becd361837e07a0dc943f78da5cac39a
