#!/bin/bash

##
# Pre-requirements:
# - env TARGET: path to target work dir
##
git clone --no-checkout https://github.com/DaveGamble/cJSON.git \
    repo
git -C repo checkout 324973008ced4ea03d1626a00915d0399ecbd9db
