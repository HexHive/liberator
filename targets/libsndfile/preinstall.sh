#!/bin/bash

DEBIAN_FRONTEND="noninteractive" \
    sudo apt-get -y install --no-install-suggests --no-install-recommends autoconf autogen automake build-essential libasound2-dev \
  libflac-dev libogg-dev libtool libvorbis-dev libopus-dev libmp3lame-dev \
  libmpg123-dev pkg-config python libogg0 libopus0 libflac8 libmp3lame0 libasound2 libvorbis0a libmpg123-0
