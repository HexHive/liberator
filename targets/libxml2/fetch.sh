#!/bin/bash

##
# Pre-requirements:
# - env TARGET: path to target work dir
##

git clone --no-checkout https://github.com/GNOME/libxml2.git \
    "$TARGET/repo"
git -C "$TARGET/repo" checkout 7846b0a677f8d3ce72486125fa281e92ac9970e8