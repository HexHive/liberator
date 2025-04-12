#!/bin/bash

targets=( "c-ares" "cjson" "cpu_features" "libaom" "libhtp" "libpcap" "libvpx" "pthreadpool" "zlib" )


for i in $( eval echo {1..$ITERATIONS} )
do
   for target in "${targets[@]}"; do
       docker run --rm --name hopper_dedup_${target}_${i} \
           --privileged \
	   -v $(pwd):/fuzz \
	   -t hopper \
	   /bin/bash -c "TARGET=$target ITER=$i ./start_dedup.sh || true" 
   done
done
