#!/bin/bash
set -e

##
# Pre-requirements:
# - env TARGET: path to target work dir
# - env OUT: path to directory where artifacts are stored
# - env CC, CXX, FLAGS, LIBS, etc...
##

source ${FUZZER}/instrument.sh

# if [ ! -d "$TARGET/repo" ]; then
#     echo "fetch.sh must be executed first."
#     exit 1
# fi

cd "$TARGET/repo"

# driver source:
PROGRAM_W_EXT=`ls $SHARED/drivers/ | grep "${PROGRAM}\.*"`
cp $SHARED/drivers/$PROGRAM_W_EXT ./fuzz/my_driver.c

DRIVER_PATCH="fuzz/my_driver: fuzz/my_driver.c \n\
\t\$(CC) -Iinclude \$(BIN_CFLAGS) \$(BIN_CPPFLAGS) -c -o \
fuzz/my_driver.o fuzz/my_driver.c \n\
\t\$\${LDCMD:-\$(CC)} \$(BIN_CFLAGS) -L. \$(BIN_LDFLAGS) \
-o fuzz/my_driver fuzz/my_driver.o -lssl -lcrypto \$(BIN_EX_LIBS)"
echo -e ${DRIVER_PATCH} >> $TARGET/repo/Makefile

# build the driver
make -j$(nproc) LDCMD="$CXX $CXXFLAGS" fuzz/my_driver

# copy the driver for later fuzzing session
cp ./fuzz/my_driver $OUT/$PROGRAM

cd -
