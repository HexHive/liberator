#!/bin/bash

DEBIAN_FRONTEND="noninteractive" \
  apt-get -y install --no-install-suggests --no-install-recommends pkgconf zlib1g zlib1g-dev libzstd1 libzstd-dev cmake  
