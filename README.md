# libErator artifact

This repository contains the code for the FSE'25 paper: [`Liberating Libraries through Automated Fuzz Driver Generation`](https://nebelwelt.net/files/25FSE2.pdf).

Purpose: libErator automatically generates drivers (unit-tests) starting from a library source.

The whole framework is composed of three main components:

- Static analyzer: it takes a library soure code an emits a list of constraints - `./condition_extractor`.
- Driver generator: it uses the library constraints (from the static analyzer) and synthetizes the drivers (+ seeds) - `./tool/main.py`.
- Fuzzing: we use slightly customized libfuzz to fuzz the new generated drivers - `./custom-libfuzzer`.

## Citation
> Flavio Toffalini, Nicolas Badoux, Zurab Tsinadze, and Mathias Payer. 2025. Liberating Libraries through Automated Fuzz Driver Generation: Striking a Balance without Consumer Code. Proc. ACM Softw. Eng. 2, FSE, Article FSE095 (July 2025), 23 pages. https://doi.org/10.1145/3729365

```bibtex
@inproceedings{Toffalini_Liberating_Libraries_through_2025,
  author = {Toffalini, Flavio and Badoux, Nicolas and Zurab, Tsinadze and Payer, Mathias},
  booktitle = {Proceedings of the ACM on Software Engineering,},
  doi = {10.1145/3729365},
  month = jul,
  volume = 2,
  publisher = {ACM New York, NY, USA},
  title = {{Liberating Libraries through Automated Fuzz Driver Generation}},
  url = {https://dx.doi.org/10.14722/3729365},
  year = {2025}
}
```
Or the cite button on the left of GitHub interface.

## How to Install

The environment has been designed for VS Code. 
The Dockerfile in the root folder builds the container, that will be used as development environment in VS Code.

**To install Docker extension and make your dev env:**

https://code.visualstudio.com/docs/remote/containers#_quick-start-open-an-existing-folder-in-a-container

**Tips to use your GH SSH from inside the Docker**

https://code.visualstudio.com/docs/remote/containers#_sharing-git-credentials-with-your-container

**If you do not remember how to Docker your user**

From [here](https://docs.docker.com/engine/install/linux-postinstall/).

TL;DR;

```bash
# if not docker group exists
$ sudo groupadd docker
$ sudo usermod -aG docker $USER
# IMPORTANT: logout/login
# IMPORTANT 2: kill/exit tmux sessions (be careful to other tmux users with open sessions)
```

**Remember to disable multithreading**

<u>Important: do not turn multithreading on, reboot the machine instead</u>

```bash
echo off | sudo tee /sys/devices/system/cpu/smt/control
```

**NSF tricks**

```bash
# install client
sudo apt install nfs-common
mkdir $LOCAL_FOLDER
sudo mount $SERVER_IP:$REMOTE_FOLDER $LOCAL_FOLDER
```

**Preliminary installation**

In the host, run the script:
```bash
./preinstall.sh
```
It will install the minimal Python packages and compile our custom libfuzzer version.

## How to inteagrate a new a target (a new library)

- [Add a new Target](./_docs/AddNewTarget.md)
- [Debug a Target in local](./_docs/DebugLocal.md)

## Specific Gudies

Ad-hoc guides for specific components of the project

- [Library Analysis](./_docs/Analysis.md)
- [Driver Generation](./_docs/DriverGeneration.md)
- [Fuzzing a Driver](./_docs/FuzzingDrivers.md)
- [Statistics](./_docs/Statistics.md)

## Internal technical details

- [Driver IR](./_docs/Driver_IR.md)

## Problems Addressed and Solved

These are the challenges that we face, and the solution proposed. We further
indicate if the solution requires manual intervention or is completely automatic.

- Correct sequence of APIs:
    - control-flow -> a valid chain of functions  
    - data-flow -> assign coherent arguments to each function
    > **automatic**: both solved with NDA, which guarantees the creation of a
    > sequence of APIs whose function + arguments match the contraints of a
    > context. The constraints are modelled as list of fields manipulated.
    - source/sink identification: depends on the type-system/philosophy used in
      the library.
    > **automatic**: we systematize a few strategies and associate a policy for
    > each of them. Each policy finds source/sink APIs. We then automatically
    > identify the most suitable policy for a library.
- Data constraints -> the arguments should adhere to some data constraints:
    - args used as a string -> add NULL to the end
    - args used as an array -> prepare an array of objects
    - args used as a file -> prepare a temporary file to store information
    - args modified by the API -> known it is an output
    - dependencies, we know two arguments are used together (e.g., in a
      if-condition or in a loop). This info allows us to define few policies:
        - arg + len: one arg is an array and another arg controls its length.
        - arg addr + arg addr: the API expects two arguments that belong to the
          same buffer argument.
    - coherent cleanup: we infer which function correctly de-allocate an object
      (i.e., `fclose(pf)`). If it is not possible, we fallback to `free()` if
      the object is allocated in heap.
    - args used for malloc-length: we cap the malloc allocation to avoid OOM
    > **automatic**: For each API's argument, we infer a set of constraints,
      which combined with some policies, allow us to automatically prepare the
      driver and increase its stability. 
- Data initialization -> some library expects the user to initialize data before
  interacting with the APIs. These operations fall beyond the API code analysis.
    - chain of objects -> the library expects the user to create a chain of
      objects that point to each other, without using any APIs
    - callbacks -> for testing reason, the user should prepare a set of
      callbacks to test specific library functionalities
    - var arg functions -> should we care of these cases (??)
    > **manual**: we require an operator to define a small set of templates to
    > be used for initializing these cases, e.g., a set of minimal callbacks, or
    > simple patterns to initialize a struct. Then our driver generator
    > leverages this info to build valid drivers. We also estimate the number of
    > manual templates required and their types.
- Useful header -> what are the headers useful for a consumer?
    > **manual**: we require an operator to indicate the public header files of
    > a library. Many headers are supposed to be private but they are installed
    > as publicly accessible, thus, it is not possible to infer which is which
    > automatically.

#
