#!/bin/bash

echo "[INFO] No Dependencies"
DEBIAN_FRONTEND="noninteractive" \
	  apt-get -y install --no-install-suggests --no-install-recommends build-essential \
	    checkinstall \
	      git \
	        autoconf \
		  automake \
		    libtool libtool-bin autopoint libdw-dev flex gawk cython3 cython pkg-config

