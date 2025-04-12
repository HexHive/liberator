# Running UTopia campaigns


Steps:
1. Build Docker image: `docker buildx build -f docker/Dockerfile -t utopia_clang12 .`
2. Build drivers: `python3 helper/create_fuzzers.py` (adjust `project_list` if needed)
3. Run fuzzing campaign: `./run_fuzzers.sh project1 project2 ...` or `./run_fuzzer.sh` to run all projects (adjust project list if needed)
4. Get coverage: `./get_coverage_data.sh`


