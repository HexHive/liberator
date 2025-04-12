#!/bin/bash

##
# Pre-requirements:
# - env TARGET: path to target work dir
##

git clone --no-checkout https://chromium.googlesource.com/chromiumos/platform/minijail \
    "$TARGET/repo"
git -C "$TARGET/repo" checkout 99e8fd4bf9aaf62eab9b3cabddc2939cb3427029
