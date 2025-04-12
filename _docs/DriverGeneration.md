# Driver Generation

The driver generation uses the information extracted from the
[analysis](./Analysis.md) plus additional setting.

- [The tool](#the-tool)
- [Configuration](#configuration)
- [End-To-End Example](#end-to-end-example)

## The tool

The main driver generator tool is in
```bash
$ ./tool/main.py
```
and it expects three arguments
- `-h` -- show the help prompt
- `--config CONFIG` -- CONFIG is a .toml file with the following [options](#configuration-file)
- `--overwrite OVERWRITE` -- this is optional, the framewokr will overwrite the
  parameters in CONFIG with the ones found in OVEWRITE. To be used to control
  the driver generation process of multiple targets without changing single
  files

## Configuration File

The configuration is composed of three sections: `analysis`, `generator`, `backend`. 

The `analysis` section takes all the files produces by the
[analysis](./Analysis.md).

The `generator` section contains parameters strictly for the driver generation:
- `workdir` -- output dir for drivers and corpus
- `policy` -- the policy to be used to generate the driver. We have two options: 
    - `constraint_based` -- applying the NDF automata algorithm
    - `only_type` -- apply a grammar based on API's types
- `dep_graph` -- type of depdendency graph, possible options:
    - `type` -- based on types
    - `undef` -- an alternative dependency graph, not good reults (experimental)
- `pool_size` -- number of drivers generated
- `driver_size` --number of APIs per driver
- `num_seeds` -- initial corpus size for reach driver
- `backend` -- the type of code produed, backend supported:
    - `libfuzz` -- the driver is compatible with LibFuzzer
    - `mock` -- pseudocode for debug

The `backend` section deals with specific backed options:
- `header` -- indicates the folder with the library headers
- `public_headers` -- indicate what header files (from `header`) must be
  included in the driver

## End-To-End Example

This is an example of driver generator for libtiff. The configuration should be
shipped with the repository and is located in `./targets/libtiff/generator.toml`.

This module is quite standard, one should adapt the `analysis` section to point
to the analysis results for a given library.

Here is an example with comments.

```toml
[analysis]
apis_llvm = ".../apis_llvm.json" # API arguments from LLVM pass
apis_clang = ".../apis_clang.json" # API aruguments from Clang ast analysis
coercemap = ".../coerce.log" # to handle 'coerce' arguments (*)
headers = ".../exported_functions.txt" # list of exported functions
incomplete_types = ".../incomplete_types.txt" # list of incomplete types
conditions = ".../conditions.json" # API constraints 
minimum_apis = ".../apis_minimized.txt" # minimize APIs
data_layout = ".../data_layout.txt" # data layout info
enum_types = ".../enum_types.txt" # enum types info

[generator]
workdir = ".../workdir/" # output dir for drivers and corpus
policy = "constraint_based" # the policy to be used to generate the driver
dep_graph = "type" # dependency graph
pool_size = 5 # number of drivers generated
driver_size = 10 # number of APIs per driver
num_seeds = 1 # initial corpus size for reach driver
backend = "libfuzz" # the driver is compatible with LibFuzzer

[backend]
headers = ".../library/include/" # header files folder
public_headers = ".../public_headers.txt" # what header files I really need to include
```

Usage:
```bash
$ ./tool/main.py --config ./targets/libtiff/generator.toml
DataLayout populate!
Generating drivers...
[...]
I have done 5 drivers!
Storing driver: driver0.cc
Storing seeds for: driver0.cc
Storing driver: driver1.cc
Storing seeds for: driver1.cc
Storing driver: driver2.cc
Storing seeds for: driver2.cc
Storing driver: driver3.cc
Storing seeds for: driver3.cc
Storing driver: driver4.cc
Storing seeds for: driver4.cc
```

This populates the `workdir`, stores the drivers into `workdir/drivers`, and an inital corpus in `workdir/corpuse/driverX`. 
Here is an example.

```bash
$ tree workdir
workdir
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


---

(*) Coerce arguments https://lists.llvm.org/pipermail/cfe-dev/2013-January/027302.html