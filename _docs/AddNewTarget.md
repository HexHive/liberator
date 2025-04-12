# Add a New Target

To add a new target one can take inspiration from `libtiff`.

**Preliminary steps**

One needs first to understand how to successfully compile a library. This may
mean to deal with different building systems, e.g., CMake, make, ninja. I
recommend to spend some time to build the library in your local machine, and run
a minimal example (a simple hello.cc that links against the library).

*What is it important?*

You need to understand:
- how to control `CFLAGS` and `CXXFLAGS`
- how to set the compiler `CC` and `CXX`
- indicate the installation folder
- compile statically, e.g., producing a `.a` file somehow

Once mastered these skills (!), you should be able to create the following
scripts.

**Create a new folder**
Add a new folder in `./target`:
```bash
NEWLIBRARY=<a-library>
mkdir -p ./target/$NEWLIBRARY
```
**Scripts**
We need *seven* scripts/files for the full pipeline:

```bash
analysis.sh
build_library.sh
fetch.sh
fuzz_driver.sh
generator.toml
preinstall.sh
public_headers.txt
```

**preinstall.sh**

The bash script runs an `apt install` (or similar) to install system dependencies.
For instance:
```bash
#!/bin/bash

apt-get update && \
    apt-get install -y git make autoconf automake libtool cmake nasm \
        zlib1g-dev liblzma-dev libjpeg-turbo8-dev wget

```
The script will be automatically invoked by `analysis.sh` and `build_library.sh`.

**fetch.sh**

This downloads the source files and stores them into `$TARGET`. You must assume
`$TARGET` is an asbolute path, a possible example is:
```bash
#!/bin/bash

git clone --no-checkout https://gitlab.com/libtiff/libtiff.git \
    "$TARGET/repo"
git -C "$TARGET/repo" checkout c145a6c14978f73bb484c955eb9f84203efcb12e
```

If the library is not in git/mercury/svn, you may want to fallback to the old
good wget+tar.

The script will be automatically invoked in the docker building.

**public_headers.txt**

The file indicates which library headers are meant to be included in the
consumer/driver. One just needs to indiates the actual file, no subfolder
handled yet.
Example:
```text
htp.h
htp_transaction.h
bstr.h
```


**analysis.sh**

This contains the steps to analyze the library and produce the meta-data for
generating the drivers later. Make sure the building system adheres to the
following set-up.

Be sure that:
- create working dir:
```bash
WORK="$TARGET/work"
rm -rf "$WORK"
mkdir -p "$WORK"
mkdir -p "$WORK/lib" "$WORK/include"
```
- Set `wllvm` as a compiler along with its respective flags. The dev container
  (i.e., the docker) should already contain a custom clang in `$LLVM_DIR`.
  Setting `CC`/`CXX` might differ for your library.
```bash
export CC=wllvm
export CXX=wllvm++
export LLVM_COMPILER=clang
export LLVM_COMPILER_PATH=$LLVM_DIR/bin
export LIBFUZZ_LOG_PATH=$WORK/apipass
```
- Make sure you create the folder where storing analysis's results
```bash
mkdir -p $LIBFUZZ_LOG_PATH
```
- Configure the library building by setting `CFLAGS` and `CXXFLAGS` and including `"-mllvm -get-api-pass -g -O0`. This step depends on the library building system.
```bash
CC=wllvm CXX=wllvm++
CXXFLAGS="-mllvm -get-api-pass -g -O0"
CFLAGS="-mllvm -get-api-pass -g -O0"
```
- Rule of thumb: create empty files to record the results:
```bash
touch $LIBFUZZ_LOG_PATH/exported_functions.txt
touch $LIBFUZZ_LOG_PATH/incomplete_types.txt
touch $LIBFUZZ_LOG_PATH/apis_clang.json
touch $LIBFUZZ_LOG_PATH/apis_llvm.json
touch $LIBFUZZ_LOG_PATH/coerce.log
```
- Compile/install, e.g., `make`/`make install`

NOTE! Sometime setting `CFLAGS`/`CXXFLAGS` is not sufficient to force `-O0`. For
Makefile, for instance, a command like that might turn out handy!
```bash
find . -name Makefile -exec sed -i 's/-O2/-O0/g' {} \;
```

- Extract `.bc` files, for instance
```bash
extract-bc -b $WORK/lib/libtiffxx.a
extract-bc -b $WORK/lib/libtiff.a
```
- Invoke header analysis, e.g.,
```bash
$TOOLS_DIR/tool/misc/extract_included_functions.py -i "$WORK/include" \
    -p "$LIBFUZZ/targets/${TARGET_NAME}/public_headers.txt" \
    -e "$LIBFUZZ_LOG_PATH/exported_functions.txt" \
    -t "$LIBFUZZ_LOG_PATH/incomplete_types.txt" \
    -a "$LIBFUZZ_LOG_PATH/apis_clang.json" \
    -n "$LIBFUZZ_LOG_PATH/enum_types.txt"
```
It is important that `-e`, `-t`, and `-a` flags refer to files in
`$LIBFUZZ_LOG_PATH`. The option `-p`, insteaed, points to the `$TARGET_NAME` in
folder.
- Run the static analyzer, e.g.,
```bash
$TOOLS_DIR/condition_extractor/bin/extractor \
    $WORK/lib/libtiff.a.bc \
    -interface "$LIBFUZZ_LOG_PATH/apis_clang.json" \
    -output "$LIBFUZZ_LOG_PATH/conditions.json" \
    -minimize_api "$LIBFUZZ_LOG_PATH/apis_minimized.txt" \
    -v v0 -t json -do_indirect_jumps \
    -data_layout "$LIBFUZZ_LOG_PATH/data_layout.txt"
```
Again, the analyzer seeks for the `.bc` extracted before, while `-interface`,
`-output`, `-minimize_api`, and `-data_layout` point to `$LIBFUZZ_LOG_PATH`.
Moreover, use always `-v v0`, `-t json`, and `-do_indirect_jumps`.


*Entry point*

`./docker/run_analysis.sh` is the analysis entry point. To run the analysis, do like:
```bash
# to run outside the docker, for local usage see (*)
cd ./docker
TARGET=libtiff ./run_analysis.sh
```

 If everything works fine, the analyzer should generate a folder in `./analysis/$TARGET_NAME`, such as:
```bash
ls ./analysis/libtiff
repo work
```
`repo` contains the cloned library source code. `work` contains the analysis
result and works as the installation folder for the library. Important folders:
```bash
ls libtiff/work/apipass # results of the analysis
apis_clang.json     conditions.json         incomplete_types.txt
apis_llvm.json      data_layout.txt         apis_minimized.txt
coerce.log          exported_functions.txt

ls libtiff/work/lib  # .a and .bc files after installation
libtiff.a  libtiff.a.bc  libtiff.la  libtiffxx.a  libtiffxx.a.bc  libtiffxx.la  pkgconfig

ls libtiff/work/include # header files / exposed functions
tiff.h  tiffconf.h  tiffio.h  tiffio.hxx  tiffvers.h
```

If you *really* want to know more regarding options etc, check [here](Analysis.md).

**generator.toml**

This controls how to generate drivers. Simplest approach: copy-paste from
`libtiff` and change the folder paths. The paths must be absolute and refer to
the in-docker file system.

**NOTE:** Remember that some parameters could be overwritten by a global
configuration.
In `$LIBFUZZ`, there is `overwrite.toml`.
```toml
[generator]
pool_size = 40
driver_size = 10
num_seeds = 20
```
`./tool/main.py` checks also this file and replaces the parameters. This is used
to control bulk-driver generation. I am sure people will get confused, so I
better write this here.

*Entry point*

After running the analysis! You can run the driver generation phase.

```bash
# to run outside the docker, for local usage see (*)
cd ./docker
TARGET=libtiff ./run_drivergeneration.sh
```
This will create a `workdir/$TARGET`, somethig like:
```bash
ls workdir/libtiff
corpus # all the initial corpus
drivers # all the drivers
```
If you want to know more of driver generation, check [here](DriverGeneration.md).

**build_library.sh**

This compiles and prepares the library to be fuzzed with libfuzzer.
We have to compile the library twice. First with fuzzing (fuzzer-no-link, ASan) instrumentation
and secondly with coverage instrumentation.
This is very similar to `analysis.sh`. The difference is in the `CFLAGS` and `CXXFLAGS` that first must be set as:

```bash
export CXXFLAGS="-fsanitize=fuzzer-no-link,address -g" \
export CFLAGS="-fsanitize=fuzzer-no-link,address -g"
```
`-fsanitize=fuzzer-no-link` prepares the library to be used in LibFuzzer, while
`-fsanitize=address` includes ASan.

While for coverage build we need:
```bash
export CXXFLAGS="-fprofile-instr-generate -fcoverage-mapping -g" \
export CFLAGS="-fprofile-instr-generate -fcoverage-mapping -g"
```

It is important to save the profile version of the library before running fuzzing build:
`mv $WORK/lib/{library_name}.a $WORK/lib/{library_name}_profile.a`


Moreover, we do not need `wllvm` here. A simpler configuration such as the following is preferable.
```bash
export CC=$LLVM_DIR/bin/clang
export CXX=$LLVM_DIR/bin/clang++
```

The rest depends on the library building system. I (aka Flavio) suggest to
copy `analysis.sh`, modify only `CC`, `CXX`, `CFLAGS`, `CXXFLAGS`, and remove the
analysis part.

Similar to `analysis.sh`, the scripts assumes `$TARGET` is an absolute path in
the system, and `$WORK` is the installation path for the library. The Dockerfile
changes the `$WORK` directory making it point to a different location. In
practice, you will have two library installations, one for analysis and another
for fuzzing. However, this should be transparent for you. Meaning you should not
care.

For more info refer to [here](FuzzingDrivers.md).

**compile_driver.sh**

This script is a simple loop that link drivers in `./workdir/${TARGET}/drivers` against the library compiled from `build_library.sh`.

Similarly, copy `compile_driver.sh` from `libtiff` and adjust the compilation step.

For reference, I left two `[TAG]` that contains the part of the script to modify
in `libtiff`'s `compile_driver.sh` script.

Similar to building library, we have to compile the driver twice: for fuzzing
and for profiling (with usual `-fprofile-instr-generate -fcoverage-mapping` flags).

The important thing is to compile drivers against the `.a` library from
`./build_library.sh` (the profile driver should be compiled against respective profile library),
and save the output in the same `.cc` folder for fuzzer and inside `profiles` folder for coverage intrumented driver.
The rest *should* work transparently.

The actual fuzzing campaign is handled by the script
`./targets/start_fuzz_driver.sh`, which will look up the correct
`compile_driver.sh` according to the `$TARGET` set.

*Entry point for compile_driver.sh and build_library.sh*

Thery are used together, just run:
```bash
# to run outside the docker, for local usage see (*)
cd ./docker
TARGET=libtiff TIMEOUT=1m DRIVER=driver8 ./run_fuzzing.sh
```
- `TARGET` -- the library to fuzz
- `TIMEOUT` -- campaign length, accepts minutes [m], seconds [s], hours [h]
- `DRIVER` -- the actual driver to fuzz, if omitted compile/fuzz all drivres
  (equivalent to `DRIVER=*`)

The script additionally creates a `crashes` folder for the, guess what, crashes!
The initial corpus is also copied in a new folder `corpus_new` to divide
generated and initial seeds.

For more info refer to [here](FuzzingDrivers.md).

---
(*) [Debug Locally](DebugLocal.md)
