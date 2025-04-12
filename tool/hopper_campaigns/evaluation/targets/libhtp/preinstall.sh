#!/bin/bash

DEBIAN_FRONTEND="noninteractive" \
    apt-get -y install --no-install-suggests --no-install-recommends autoconf autotools-dev automake libtool
