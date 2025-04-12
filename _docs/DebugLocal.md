# Debug Local



## Driver/Crash Locations

All the drivers and the campaign results are located in a `workdir` folder. The
folder name depends on the actual configuration, and has this structure
`workdir_${n_driver}_${n_api}`. Meaning `workdir_20_2` contains 20 drivers with
2 APIs each. All the information regarding a specific library are in some
subfolder like `workdir_${n_driver}_${n_api}/{target_name}`. For instance,
`workdir_20_2/libvpx` contains drivers, crasehs, and coverage information
regarding libvpx (with 20 driver/2 APIs configuraiton).

```bash
cd ${LIBFUZZER_HOME}/fuzzing_campaigns
# all the drivers for libvpx with configuration 20 drivers/2 APIs
ls workdir_20_2/libvpx/drivers
# all the crashes from the first run 
ls workdir_20_2/libvpx/results/iter_1/crashes/
# all the clustered crashes for driver0
ls workdir_20_2/libvpx/clusters/driver0/
```

## Reproduce a crash

To reproduce a crash, one has to (1) select a driver and a specific crash, (2) run the driver against the crashing input. For instance, to replicate a crash for `driver1` for `libvpx` on `workdir_20_2`, one can run:
```bash
cd ${LIBFUZZER_HOME}/fuzzing_campaigns/workdir_20_2/libvpx
./drivers/driver1 ./results/iter_1/crashes/driver1/crash...
# ASAN report (hopefully)
```

The unique crashes are in the `cluster` subfoder, thus the following to replicate them.
```bash
cd ${LIBFUZZER_HOME}/fuzzing_campaigns/workdir_20_2/libvpx
./drivers/driver1 ./results/clusters/driver1/cl1/crash...
# ASAN report (hopefully)
```
**NOTE**: The class `clx` is automatically assigned. We group the crashes from
all the runs of a campaign by using a stack trace approach (more in the paper).

## Debugging a crash

There are two ways to debug a crash.

**Debug with ASAN instrumentation**:  
Use GDB directly against the driver and the crash under analysis. The
drivers are compiled with ASAN by default. Therefore we need some small
adjustment.

From bash, run
```bash
gdb --arg ./drivers/driver1 ./path_to_crash/crash
```
Then, in GDB.
```bash
# sometime GDB-PEDA sets follow-fork-mode = child by default
set follow-fork-mode parent
# this allows GDB to intercept ASAN [1]
set ASAN_OPTIONS=abort_on_error=1
run
```
From this point, GDB should stop at the crashing point. Good luck from here!


**Debug without ASAN instrumentation**:  
If you want to get rid of ASAN instrumentation (and having a cleaner asm code).
You have to compile the library and the driver not for fuzzing and repeat the
same operation from above. It could be that the bug is impossible to reproduce
without ASAN tho.  
**TODO:** document how to build library/drivers w/o ASAN.


**Debug environment**:

We also provided a debug container to help you set up the minimal environment.
```bash
cd $LIBFUZZ_HOME
./start_debugenv.sh $TARGET_NAME
```

Where `TARGET_NAME` is one of the project in the `./target` folder.


<hr />
[1] https://github.com/google/sanitizers/wiki/SanitizerCommonFlags