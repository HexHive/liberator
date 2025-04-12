#!/bin/bash


targets=( "c-ares" "cjson" "cpu_features" "libaom" "libhtp" "libpcap" "libtiff" "libvpx" "minijail" "pthreadpool" "zlib" )

build_library() {
    for target in "${targets[@]}"; do
	    docker run --rm --name hopper_build_lib_$target \
	    --privileged \
	    -v $(pwd):/fuzz \
	    -t hopper \
	    /bin/bash -c "TARGET=$target ./start_build.sh"
    done
}


build_fuzzer() {
    for target in "${targets[@]}"; do
	echo "Building $target"
	docker run --rm --name hopper_build_fuzzer_$target \
	    --privileged \
	    -v $(pwd):/fuzz \
	    -t hopper \
	    /bin/bash -c "cd $target && hopper compile"
    done
}


fuzz() {
   cpu_id=0
   for target in "${targets[@]}"; do
	docker run --rm --name hopper_fuzz_$target \
	    --cpuset-cpus $cpu_id \
	    --privileged \
	    -v $(pwd):/fuzz \
	    -d hopper \
	    /bin/bash -c "TARGET=$target TIMEOUT=$TIMEOUT ./start_fuzzing.sh"
	cpu_id=$(( cpu_id + 1 ))
    done
    cpu_id=0
}


build_library

for i in $( eval echo {1..$ITERATIONS} )
do
    build_fuzzer
    fuzz
    sleep $TIMEOUT
    sleep 10m # just in case
    for target in "${targets[@]}";do
    	mv $target/output $target/output_$i
    done
done
