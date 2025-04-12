#!/bin/bash


UTOPIA_DOCKER_IMAGE="utopia_clang12"

projects=()

if [ $# -ne 0 ]; then
  projects=$@
else
  projects=( "cpu_features" "libaom" "libhtp" "libvpx" "minijail" "pthreadpool" )
fi

docker run --rm -v $(pwd):/root/fuzz-drivers-evaluation/utopia -it $UTOPIA_DOCKER_IMAGE /bin/bash -c "cd /root/fuzz-drivers-evaluation/utopia && ./helper/get_coverage_data_helper.sh"
