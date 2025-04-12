#!/bin/bash
#  mkdir -p workdir_X_X/{cpu_features,libtiff,minijail,pthreadpool,libaom,libvpx,libhtp,libpcap,c-ares,zlib,cjson}/iter_{1,2,3,4,5}


# for p in "cpu_features" "libtiff" "minijail" "pthreadpool" "libaom" "libvpx" "libhtp" "libpcap" "c-ares" "zlib" "cjson"; do
#     for i in 1 2; do
#         # d=$((i+3))
#         echo "$p from $i to $d"
#         # scp -t flavio@hexhive012.iccluster.epfl.ch:/media/hdd0/toffalin/main/fuzzing_campaigns/gen24_deep0/workdir_X_X/$p/iter_$i/paths_observed.txt workdir_X_X/$p/iter_$d/
#         scp -r flavio@hexhive012.iccluster.epfl.ch:/media/hdd0/toffalin/main/fuzzing_campaigns/gen24_deep0/workdir_X_X/$p/iter_$i/coverage_data/ workdir_X_X/$p/iter_$i/coverage_data/
#     done 
#     # scp -r toffalin@hexhive001.iccluster.epfl.ch:/media/hdd0/toffalin/main/fuzzing_campaigns/gen24_deep0/workdir_X_X/$p/iter_1/coverage_data/ workdir_X_X/$p/iter_1/coverage_data
# done

for p in "cpu_features" "libtiff" "minijail" "pthreadpool" "libaom" "libvpx" "libhtp" "libpcap" "c-ares" "zlib" "cjson"; do
    for i in 1 2; do
        d=$((i+3))
        echo "$p from $i to $d"
        # scp -t flavio@hexhive012.iccluster.epfl.ch:/media/hdd0/toffalin/main/fuzzing_campaigns/gen24_deep0/workdir_X_X/$p/iter_$i/paths_observed.txt workdir_X_X/$p/iter_$d/
        # scp -r flavio@hexhive012.iccluster.epfl.ch:/media/hdd0/toffalin/main/fuzzing_campaigns/gen24_deep0/workdir_X_X/$p/iter_$i/coverage_data/ workdir_X_X/$p/iter_$i
        # mv workdir_X_X/$p/iter_$i/coverage_data/coverage_data/* workdir_X_X/$p/iter_$i/coverage_data/
        # rmdir workdir_X_X/$p/iter_$i/coverage_data/coverage_data
    done 
    # scp -r toffalin@hexhive001.iccluster.epfl.ch:/media/hdd0/toffalin/main/fuzzing_campaigns/gen24_deep0/workdir_X_X/$p/iter_1/coverage_data/ workdir_X_X/$p/iter_1/coverage_data
done