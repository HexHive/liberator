# Running Hopper Campaigns

1. Clone Hopper repo from `https://github.com/FuzzAnything/Hopper` (at the time of writing this @ da5e044 commit)
2. Copy `hopper`, `Dockerfile` and `update_clang.sh` to `Hopper` directory
3. Build Hopper: `docker build -t hopper ./Hopper`
4. Follow below steps:

```bash
cd evaluation/targets
export ITERATIONS=5
export TIMEOUT=24h

# before running these adjust set of targets in the scripts
./run_fuzzing_all.sh
./run_coverage_all.sh
./run_deduplication_all.sh
```
