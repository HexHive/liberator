#!/bin/bash


targets=( "c-ares" "cjson" "cpu_features" "libaom" "libhtp" "libpcap" "libtiff" "libvpx" "minijail" "pthreadpool" "zlib" )




for i in $( eval echo {1..$ITERATIONS} )
do
  for target in "${targets[@]}"; do
	docker run --rm --name hopper_build_prof_${target}_${i} \
	    --privileged \
	    -v $(pwd):/fuzz \
	    -t hopper \
	    /bin/bash -c "TARGET=$target ITER=$i ./start_profile_build.sh"
   done
done
for i in $( eval echo {1..$ITERATIONS} )
do
   for target in "${targets[@]}"; do
       docker run --rm --name hopper_cov_${target}_${i} \
           --privileged \
	   -v $(pwd):/fuzz \
	   -t hopper \
	   /bin/bash -c "TARGET=$target ITER=$i ./start_coverage.sh || true" 
   done
done
