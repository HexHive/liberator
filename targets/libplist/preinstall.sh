#!/bin/bash

DEBIAN_FRONTEND="noninteractive" \
  sudo apt-get -y install --no-install-suggests --no-install-recommends build-essential \
  checkinstall \
  git \
  autoconf \
  automake \
  libtool-bin autopoint libdw-dev flex gawk cython3 cython
