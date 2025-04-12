
# Library Analysis

The analysis part is composed of these parts:
- [Preliminary](#preliminary)
- [LLVM pass](#llvm-pass)
- [Extract Exported Functions](#extract-exported-functions)
- [Condition Extractor](#condition-extractor)
- [End-to-End Example](#end-to-end-example)

## Preliminary

Set the env variable `LIBFUZZ_LOG_PATH` that will contain all the library results.
```bash
export LIBFUZZ_LOG_PATH=$WORK/apipass
```

## LLVM Pass

The exact steps to use this pass depends on the actual library building system.

The library should be compiled with a combination `wllvm` and a custom LLVM
pass. The LLVM pass is shipped in the `LLVM` folder and is compiled/embedded in
the repository clang when the Docker builds. 
 
The LLVM pass analysis is activated by using the new options `-mllvm
-get-api-pass` against hte shipped clang in this repo. `$LLVM_DIR` points to the
LLVM installation in the Docker container.

Depending on the library building tool, we should set the following variables:

```bash
export CC=wllvm
export CXX=wllvm++
export LLVM_COMPILER=clang
export LLVM_COMPILER_PATH=$LLVM_DIR/bin
```
Since the pass appends logs, clean the following files before compiling, e.g.,
```bash
rm -f $LIBFUZZ_LOG_PATH/apis_llvm.json
rm -f $LIBFUZZ_LOG_PATH/coerce.log
```
Set `$CFLAG` and `$CXXFLAG`, this steps depends on the library
building tool.  
A possible set-up is:
```bash
export CFLAGS="-mllvm -get-api-pass"
export CXXFLAGS="-mllvm -get-api-pass"
```
Compile the library, locate the exported `.so`/`.a` files, and convert them
into `.bc`, e.g.,
```bash
extract-bc -b $WORK/lib/libtiffxx.a
extract-bc -b $WORK/lib/libtiff.a
```

## Extract Exported Functions

The exported functions are extracted by analyzing only the header files through:
```bash
./tool/misc/extract_included_functions.py
```
Options:
- `-h` -- show the help prompt
- `-i/include_folder <folder path>` -- folder containing the shipped library
  header files
- `-p/public_headers <file path>` -- list of public header to be actually
  included in the driver
- `-e/exported_functions <flie path>` -- output file containing the exported
  functions from `-i`
- `-t/incomplete_types <flie path>` -- output file containing the incomplete
  types
- `-a/apis_list <flie path>` -- output file containing the exported functions
  from `-i` plus argument information
- `-n/-enum_list <file_path>` -- contains enum types

NOTE: we need both `apis_list` and `exported_functions`, just trust me  
NOTE2: not all the the shipped headers (`include_folder`) are meant to be
included in the cunsumer/driver. Therefore, we require the developer to indicate
the actual list of public headers (`public_headers`).

Example of usage:
```bash
$LIBFUZZ/tool/misc/extract_included_functions.py \
    -i "$WORK/include" \
    -p "$LIBFUZZ/targets/${TARGET_NAME}/public_headers.txt" \
    -e "$LIBFUZZ_LOG_PATH/exported_functions.txt" \
    -t "$LIBFUZZ_LOG_PATH/incomplete_types.txt" \
    -a "$LIBFUZZ_LOG_PATH/apis_clang.json" \
    -n "$LIBFUZZ_LOG_PATH/enum_types.txt"
```

## Condition Extractor

The analyzer is in `./condition_extractor` folder and extract fields constraints plus other rinformation.

Preparation and compilation:
```bash
cd condition_extractor
./bootstrap.sh
make
```
Output:
```bash
./bin/extractor
```

Options:
- \<arg1\> -- a `.bc` file containing LLVM bit code
- `-h` -- show the help prompt
- `-interafce <flie path>` -- analyze all the APIs extracted from `./extract_included_functions.py` (e.g., `-interafce apis_clang.json`)
- `-function <string>` -- limit the analysis on a single function indicated as string (e.g., `-function TIFFCheckpointDirectory`)
- `-output <file path>` -- output file containing the field's constraints (e.g., `-output condition.json`)
- `-v [v0|v1|v2|v3]` -- verbosisty:
    - `v0` - No verbose (smallest `-output` file)
    - `v1` - Report ICFG nodes
    - `v2` - Report Paths if `-debug_condition` is met (experimental)
    - `v3` - To implement, no effect at the moment
- `-debug_condition <cond>` - Specific condition to be intercepted, used to print specific debug information (experimental -- very hacky!)
- `-t [txt|json|stdo]` -- output type:
    - `txt` - Text file in `-output`
    - `json` - Json file in `-output`, this is the expected format for the driver generator
    - `stdo` - Into stdout, `-output` ingored
- `-do_indirect_jumps` -- consider indirect jumps in the analysis. Stop the exploration at the indirect jumps if omitted.
- `-minimize_api <file path>` - extract minimal set of APIs to test (e.g., `-minimize_api apis_minimized.txt`)
- `-data_layout <file path>` - dump daya layout information (e.g., `-data_layout data_layout.txt`)

Options for Dominator, very experimental, don't use in production:
- `-dom` - Use Post/Dominators, very slow, no correctness guaranteed (experimental)
- `-print_dom` -- Print the Post/Dominators in .dot format, super slow, class NP hard. Just don't use it (experimental)
- `-cache_folder <path>` -- cache folder for incremental Post/Dominator analysis


Example of usage:
```bash
./bin/extractor $INSTALLATION_DIR/libtiff.a.bc \
    -interface "$LIBFUZZ_LOG_PATH/apis_clang.json" \
    -output "$LIBFUZZ_LOG_PATH/conditions.json" \
    -v v0 -t json -do_indirect_jumps \
    -minimize_api "$LIBFUZZ_LOG_PATH/apis_minimized.txt" \
    -data_layout "$LIBFUZZ_LOG_PATH/data_layout.txt"
```

## End-to-End Example

This is an example of analysis/compilation for libtiff. The file should be shipped with the repository and is located in `./targets/libtiff/analysis.sh`.

The actual wiring with different building systems is not covered here.
Some parts might differ for simplicity, please refer to the original script for more info.


```bash
#!/bin/bash

# project path
export LIBFUZZ=/workspaces/libfuzz/
# target location
export TARGET=$LIBFUZZ/analysis/libtiff/ 

# download source
./fetch.sh

# working directing, where the library will be installed
WORK="$TARGET/work"
rm -rf "$WORK"
mkdir -p "$WORK"
mkdir -p "$WORK/lib" "$WORK/include"

# setting for LLVM Pass
export CC=wllvm
export CXX=wllvm++
export LLVM_COMPILER=clang
export LLVM_COMPILER_PATH=$LLVM_DIR/bin

# location for analysis results 
export LIBFUZZ_LOG_PATH=$WORK/apipass
mkdir -p $LIBFUZZ_LOG_PATH

# precompilation
echo "make 1"
cd "$TARGET/repo"
./autogen.sh
echo "./configure"
./configure --disable-shared --prefix="$WORK" \
                                CC=wllvm CXX=wllvm++ \
                                CXXFLAGS="-mllvm -get-api-pass -g -O0" \
                                CFLAGS="-mllvm -get-api-pass -g -O0"

# prepare empty files for next analysis
touch $LIBFUZZ_LOG_PATH/exported_functions.txt
touch $LIBFUZZ_LOG_PATH/incomplete_types.txt
touch $LIBFUZZ_LOG_PATH/apis_clang.json
touch $LIBFUZZ_LOG_PATH/apis_llvm.json
touch $LIBFUZZ_LOG_PATH/coerce.log

# actual compilation step
echo "make clean"
make -j$(nproc) clean
echo "make"
make -j$(nproc)
echo "make install"
make install

# extract .bc files
extract-bc -b $WORK/lib/libtiffxx.a
extract-bc -b $WORK/lib/libtiff.a

# extract the exported functions in a file
$LIBFUZZ/tool/misc/extract_included_functions.py \
    -i "$WORK/include" \
    -p "$LIBFUZZ/targets/${TARGET_NAME}/public_headers.txt" \
    -e "$LIBFUZZ_LOG_PATH/exported_functions.txt" \
    -t "$LIBFUZZ_LOG_PATH/incomplete_types.txt" \
    -a "$LIBFUZZ_LOG_PATH/apis_clang.json" \
    -a "$LIBFUZZ_LOG_PATH/enum_types.txt"

# extract fields dependency from the library itself, repeat for each object produced
$LIBFUZZ/condition_extractor/bin/extractor \
    $WORK/lib/libtiff.a.bc \
    -interface "$LIBFUZZ_LOG_PATH/apis_clang.json" \
    -output "$LIBFUZZ_LOG_PATH/conditions.json" \
    -minimize_api "$LIBFUZZ_LOG_PATH/apis_minimized.txt" \
    -v v0 -t json -do_indirect_jumps \
    -data_layout "$LIBFUZZ_LOG_PATH/data_layout.txt"
```