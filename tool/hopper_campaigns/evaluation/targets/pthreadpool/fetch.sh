#!/bin/bash

##
# Pre-requirements:
# - env TARGET: path to target work dir
##

git clone --no-checkout https://android.googlesource.com/platform/external/pthreadpool \
    "$TARGET/repo"
git -C "$TARGET/repo" checkout f355e616e15b366dae115c916ef19e3b70327ad5
