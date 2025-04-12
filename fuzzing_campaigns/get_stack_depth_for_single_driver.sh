#!/bin/bash

if [ $# -ne 4 ]
  then
    echo "Usage: ./get_stack_depth_for_single_driver.sh \$work_dir \$project \$driver \$iter"
    echo "Example: ./get_stack_depth_for_single_driver.sh workdir_20_4 cpu_features driver8 1"
    exit 1
fi

work_dir=$1
project=$2
fuzzer=$3
iter=$4

mkdir -p ./traces/${work_dir}/${project}/${fuzzer}/iter_${iter}
python3 ../tool/misc/stack_depth/stacktrace.py ${work_dir} ${project} ${fuzzer} ${iter}

docker run \
    --rm \
    -u root \
    --privileged \
    --shm-size=2g \
    --cap-add=SYS_PTRACE \
    --security-opt seccomp=unconfined \
    --name ${work_dir}-${project}-${fuzzer}-${iter} \
    -v $(pwd):/fuzzing_campaigns \
    -t libpp-fuzzing-${project} \
    /bin/bash -c "cd /fuzzing_campaigns && gdb -x ./traces/${work_dir}/${project}/${fuzzer}/iter_${iter}/gdb_commands -batch"

docker wait ${work_dir}-${project}-${fuzzer}-${iter}
python3 ../tool/misc/stack_depth/get_max_stack_depth_and_apis.py ${work_dir} ${project} ${fuzzer} ${iter} > ./traces/${work_dir}/${project}/${fuzzer}/iter_${iter}/max_depth
echo "Output file: ./traces/${work_dir}/${project}/${fuzzer}/iter_${iter}/max_depth"
rm -f default.profraw
