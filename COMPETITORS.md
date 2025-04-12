
# Running UTopia campaigns


Steps:
1. Build Docker image: `docker buildx build -f docker/Dockerfile -t utopia_clang12 .`
2. Build drivers: `python3 helper/create_fuzzers.py` (adjust `project_list` if needed)
3. Run fuzzing campaign: `./run_fuzzers.sh project1 project2 ...` or `./run_fuzzer.sh` to run all projects (adjust project list if needed)
4. Get coverage: `./get_coverage_data.sh`

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
