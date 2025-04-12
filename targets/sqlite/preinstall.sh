#!/bin/bash

echo "[INFO] No Dependencies"
DEBIAN_FRONTEND="noninteractive" \
    sudo apt-get -y install --no-install-suggests --no-install-recommends tclsh
