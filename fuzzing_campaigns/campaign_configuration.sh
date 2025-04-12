#!/bin/bash

export PROJECTS=( "cpu_features" "libtiff" "minijail" "pthreadpool" "libaom" "libvpx" "libhtp" "libpcap" "c-ares" "zlib" "cjson" "libdwarf" "libsndfile" "libplist" "libucl" )
# trick to make ${PROJECTS} visible outside
export PROJECTS_STRING=$(IFS=:; echo "${PROJECTS[*]}")
export NUM_OF_DRIVERS=( 40 )
export NUM_OF_APIs=( 2 4 8 16 32  )
export NUM_OF_SEEDS=1
export POLICY="constraint_based"
# export MAX_CPUs=6
export MAX_CPUs=$(($(nproc) - 1))
# used w/ CONF=minimized
export USE_CUSTOM_APIS=0
# used w/ CONF=long
export USE_PER_LIBRARY_TIMEBUDGET=0

export BIAS="field_sum" # none, api_frequency, seed_number, field_inter, field_sum

case $CONF in

  quickcamp)
    export NUM_OF_DRIVERS=( 20 ) 
    export NUM_OF_APIs=( 5 )
    export TIMEOUT=10m
    export ITERATIONS=1
    ;;

  regtest)
    export TIMEOUT=0
    ;;

  selection)
    export TIMEOUT=5m
    export ITERATIONS=1
    ;;

  long)
    export USE_PER_LIBRARY_TIMEBUDGET=1
    export ITERATIONS=1
    ;;

  fuzzgen)
    export PROJECTS=( "libaom" "libvpx" )
    # export PROJECTS=( "libvpx" )
    export NUM_OF_DRIVERS=( XX  )
    export NUM_OF_APIs=( X  )
    export TIMEOUT=24h
    export ITERATIONS=5
    export USE_PER_LIBRARY_TIMEBUDGET=1
    ;;

  bestconf)
    export PROJECTS=( "libaom" "libvpx" "libhtp" "libtiff" "minijail" )
    export NUM_OF_DRIVERS=( 20  )
    export NUM_OF_APIs=( 4 8  )
    export TIMEOUT=1h
    export ITERATIONS=1
    ;;
    
  ossmanual)
    export PROJECTS=( "libdwarf" "libsndfile" "libucl"  "libplist" )
    export NUM_OF_DRIVERS=( XX  )
    export NUM_OF_APIs=( X  )
    export TIMEOUT=24h
    export ITERATIONS=5
    export USE_PER_LIBRARY_TIMEBUDGET=1
    ;;
  
  ossllm)
    export PROJECTS=( "cjson" "libpcap" "libsndfile" "libucl" "libdwarf" "libplist" )
    export NUM_OF_DRIVERS=( XX  )
    export NUM_OF_APIs=( X  )
    export TIMEOUT=24h
    export ITERATIONS=5
    export USE_PER_LIBRARY_TIMEBUDGET=1
    ;;

  minimized)
    export PROJECTS=( "libaom" "libvpx" "libhtp" "libtiff" "libpcap" "c-ares" "zlib" "cjson" )
    # probably we can fix the number of drivers to match 24 hours
    export NUM_OF_DRIVERS=( 24  )
    export NUM_OF_APIs=( 4 8 )
    export TIMEOUT=30m
    export ITERATIONS=1
    export USE_CUSTOM_APIS=1
    ;;

  search)
    export PROJECTS=( "libaom" "libvpx" "libhtp" "libtiff" "libpcap" "c-ares" )
    export POLICY="constraint_based_search"
    export NUM_OF_DRIVERS=( 20 )
    export NUM_OF_APIs=( 4 8 )
    export TIMEOUT=30m
    export ITERATIONS=1
    export USE_CUSTOM_APIS=1
    ;;

  grammar)
    export TIMEOUT=24h
    export ITERATIONS=5
    export POLICY="constraint_based_grammar"
    # NOTE: these Xs need for run_coverage.sh and run_custer.sh
    export NUM_OF_DRIVERS=( "X" )
    export NUM_OF_APIs=( "X" )
    export NUM_OF_API_GRAMMAR=10
    export NUM_OF_UNKNOWN_API=0
    export GRAMMAR_MODE=1
    # export API_PERC_UPPERBOUND=90
    # export GEN_DRIV_UPPERBOUND=4h
    # export DEEP_TIMEOUT=5m
    ;;

  grammar_quick)
    export TIMEOUT=4h
    export ITERATIONS=1
    export POLICY="constraint_based_grammar"
    # NOTE: these Xs need for run_coverage.sh and run_custer.sh
    export NUM_OF_DRIVERS=( "X" )
    export NUM_OF_APIs=( "X" )
    export NUM_OF_API_GRAMMAR=10
    export NUM_OF_UNKNOWN_API=0
    export GRAMMAR_MODE=1
    # export API_PERC_UPPERBOUND=90
    # export GEN_DRIV_UPPERBOUND=4h
    # export DEEP_TIMEOUT=5m
    ;;


  grammar_quick_nobias)
    export TIMEOUT=4h
    export ITERATIONS=1
    export POLICY="constraint_based_grammar"
    # NOTE: these Xs need for run_coverage.sh and run_custer.sh
    export NUM_OF_DRIVERS=( "X" )
    export NUM_OF_APIs=( "X" )
    export NUM_OF_API_GRAMMAR=10
    export NUM_OF_UNKNOWN_API=0
    export GRAMMAR_MODE=1
    export BIAS="none"
    # export API_PERC_UPPERBOUND=90
    # export GEN_DRIV_UPPERBOUND=4h
    # export DEEP_TIMEOUT=5m
    ;;

  grammarminimized)
    export PROJECTS=( "libaom" "libvpx" "libhtp" "libtiff" "libpcap" "c-ares" "zlib" "cjson" )
    # unset $PROJECTS_STRING
    export PROJECTS_STRING=$(IFS=:; echo "${PROJECTS[*]}")
    export TIMEOUT=24h
    export ITERATIONS=1
    export POLICY="constraint_based_grammar"
    # NOTE: these Xs need for run_coverage.sh and run_custer.sh
    export NUM_OF_DRIVERS=( "X" )
    export NUM_OF_APIs=( "X" )
    export NUM_OF_API_GRAMMAR=10
    export NUM_OF_UNKNOWN_API=0
    export GRAMMAR_MODE=1
    export USE_CUSTOM_APIS=1
    ;;

  *)
    echo -n "unknown CONF=${CONF}"
    exit 1
    ;;
esac

# LOG the configuration
LOG_FILE=config.txt
date >> $LOG_FILE
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
echo "$SCRIPTPATH/$0" >> $LOG_FILE
printf '%*s\n' "${COLUMNS:-$(tput cols)}" '' | tr ' ' - >> $LOG_FILE
env >> $LOG_FILE
