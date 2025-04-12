#!/bin/bash

##
# Pre-requirements:
# - env TARGET: path to target work dir
##
git clone --no-checkout https://github.com/the-tcpdump-group/libpcap.git \
    "$TARGET/repo"
git -C "$TARGET/repo" checkout b13fd42b1ebd3386985728286a92d9720ee89113
