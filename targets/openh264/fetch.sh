#!/bin/bash

##
# Pre-requirements:
# - env TARGET: path to target work dir
##

git clone --no-checkout https://github.com/cisco/openh264.git \
    "$TARGET/repo"
git -C "$TARGET/repo" checkout ca0e43e864c8c57ec76a7763af6436be4e76c8d0
