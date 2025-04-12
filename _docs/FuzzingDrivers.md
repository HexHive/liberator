# Fuzzing Drivers

The driver is based on [LibFuzzer](https://llvm.org/docs/LibFuzzer.html).

First, prepare the library by setting the flags `CXXFLAGS` and `CLAGS`
accordingly, for instance:
```bash
export CXXFLAGS="-fsanitize=fuzzer-no-link,address -g" \
export CFLAGS="-fsanitize=fuzzer-no-link,address -g"
```
`-fsanitize=fuzzer-no-link` prepares the library to be used in LibFuzzer, while
`-fsanitize=address` includes ASan.


Then, compile a driver against the library. 

```bash
$CXX -g -std=c++11  -fsanitize=fuzzer,address -I${INSTALL_DIR}/include \
    ./workdir/${TARGET}/drivers/driver$i.cc ${INSTALL_DIR}/libtiff.a \
    ${INSTALL_DIR}/libtiffxx.a -lz -ljpeg -Wl,-Bstatic -llzma -Wl,-Bdynamic \
    -lstdc++ -o ./workdir/${TARGET}/drivers/driver$i
 ```

Usually, a driver is shipped with a minimal corpus. Given `TARGET` the library
to test, the respective drivers and corpus should be located in:
```bash
workdir
`-- ${TARGET}
    |-- corpus
    |   |-- driver0
    |   |   `-- seed1.bin
    |   |-- driver1
    |   |   `-- seed1.bin
    |   |-- driver2
    |   |   `-- seed1.bin
    |   |-- driver3
    |   |   `-- seed1.bin
    |   `-- driver4
    |       `-- seed1.bin
    `-- drivers
        |-- driver0.cc
        |-- driver1.cc
        |-- driver2.cc
        |-- driver3.cc
        `-- driver4.cc
```

Once compiled, it is possible to run a fuzzing campaing in this way:
```bash
DRIVER_PATH=${LIBFUZZ}/workdir/${TARGET}/drivers/driver0
CORPUS_PATH=${LIBFUZZ}/workdir/${TARGET}/corpus/driver0
CRASHES_DIR=${LIBFUZZ}/workdir/${TARGET}/crashes
timeout 1h ${DRIVER_PATH} \
        ${CORPUS_PATH} \
        -artifact_prefix ${CRASHES_DIR}
```
The fuzzer/driver will run for 1h, generate new seeds in `CORPUS_PATH`, and
store the crashes in `CRASHES_DIR`.

**Fork-Mode:**  
The default behavior of LibFuzzer is to run until the first exeption is
encountered. One can use
[fork-mode](https://llvm.org/docs/LibFuzzer.html#fork-mode) and
`-ignore_crashes` to keep the fuzzing session going on. Caviat, if fork-mode is
used, one need to kill the process. For instance:
```bash
DRIVER_PATH=${LIBFUZZ}/workdir/${TARGET}/drivers/driver0
CORPUS_PATH=${LIBFUZZ}/workdir/${TARGET}/corpus/driver0
CRASHES_DIR=${LIBFUZZ}/workdir/${TARGET}/crashes
${DRIVER_PATH} ${CORPUS_PATH} -artifact_prefix ${CRASHES_DIR} \
    -fork=1 -ignore_crashes
[fuzzing...]
```
In a separae shell (or with background processes):
```bash
sleep 1h pkill -9 ${DRIVER_PATH} # or the process name
```
This will kill (aka stop the fuzzing campaign) after 1h. Seeds and crashes wll
be saved in `CORPUS_PATH` and `CRASHES_DIR`, respectively.