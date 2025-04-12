#!/bin/bash

##
# Pre-requirements:
# - env TARGET: path to target work dir
##

git clone --no-checkout https://github.com/davea42/libdwarf-code.git \
    "$TARGET/repo"
git -C "$TARGET/repo" checkout ed74b438dcbbf74759a15324c93d924191823ea7
