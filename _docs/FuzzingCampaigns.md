# Fuzzing Campaigns

To run bigger fuzzing campaigns have a look at `fuzzing_campaigns` directory.
First of all you have to modify `campaign_configuration.sh` to set you desired
targets (they should already be added as described in [AddNewTarget.md](./AddNewTarget.md)),
different number of generated drivers, number of APIs used inside the driver, number of seeds
in the initial corpus, timeout, and number of fuzzing iterations.

After everything is set, you can run
```bash
./run_analysis.sh
./run_generate_drivers.sh
./run_fuzzing.sh
./run_coverage.sh
./run_clustering.sh
```

This steps should work seemlessly and inside `workdir_X_Y` folders you will get clustered crashes
and coverage data.

Moreover, running `./post_process.sh` will generate a file with coverage and crash statistics for each fuzzer run.
