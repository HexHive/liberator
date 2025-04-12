# Fuzzing Drivers

The driver is based on [LibFuzzer](https://llvm.org/docs/LibFuzzer.html), and
the whole process is dockerized.

The bash script that orchestrates the process is `./docker/run_fuzzing.sh`.
One must provides three environment variables:
```bash
TARGET=libtiff  # target name
TIMEOUT=10s     # fuzzing time
DRIVER=driver0  # specify the driver to fuzz.
                # If omitted, it fuzzes all the produced drivers
```
The fuzzer expects a folder as such:
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

**NOTE:** To integrate `-fork` mode and `pkill` after timeout.

Example of Usage:

```bash
cd docker
TARGET=libtiff TIMEOUT=10s DRIVER=driver0 ./run_fuzzing.sh
```