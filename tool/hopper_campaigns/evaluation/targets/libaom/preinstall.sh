#!/bin/bash

echo "[INFO] Installing yasm"
DEBIAN_FRONTEND="noninteractive" \
    apt-get -y install --no-install-suggests --no-install-recommends cmake git perl yasm
