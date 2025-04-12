#!/bin/bash

##
# Pre-requirements:
# - env TARGET: path to target work dir
##

git clone https://chromium.googlesource.com/webm/libvpx \
    "$TARGET/repo"
git -C "$TARGET/repo" checkout fd84dccd511f6db3a0aa666e52ee62b7b1699d64
