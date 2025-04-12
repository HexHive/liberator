#!/usr/bin/python3

import subprocess, itertools, os, sys, multiprocessing, argparse, traceback

global base_dir
base_dir = os.getcwd()
PROJECT_FOLDER=f"{base_dir}/.."
sys.path.append(PROJECT_FOLDER)
import tool.misc.cluster as clst

is_debug = False

tot_api = {
    "pthreadpool": 30,
    "libaom": 47,
    "zlib": 88,
    "c-ares": 126,
    "cpu_features": 7,
    "libpcap": 88,
    "cjson": 78,
    "libvpx": 35,
    'libtiff': 197,
    "minijail": 97,
    "libhtp": 251
}
def source_bash_file(file_path):
    """Sources a bash file and returns the environment variables."""
    command = f"source {file_path} && env"
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True, executable='/bin/bash')
    output, _ = proc.communicate()
    env_vars = {}
    for line in output.decode().splitlines():
        key, value = line.split('=', 1)
        env_vars[key] = value
    return env_vars

def kick_fuzzing_camp(project, iteration, driver_name, cpu_id, 
                      time_plateau = None, driver_timeout = "5m", 
                      message = ""):
    
    global base_dir
    
    if message:
        print(f"[INFO] Fuzzing {driver_name} for {driver_timeout} [{message}]")
    else:
        print(f"[INFO] Fuzzing {driver_name} for {driver_timeout}")
    
    # working dir -- in the docker
    result_folder = os.path.join(os.sep, "workspaces", "libfuzz", "fuzzing_campaigns", 
                                "workdir_X_X", project, f"iter_{iteration}")
    
    # where the drivers are saved
    driver_folder = os.path.join(result_folder, "drivers")
    
    feedback_file = os.path.join(result_folder, "feedback.txt")
    
    # driver_timeout = "5m"
    
    pwd = f"{base_dir}/.."
    
    # --env LLVM_DIR={llvm_dir}
    
    cov_plateau_timeout = ""
    if time_plateau is not None:
        cov_plateau_timeout = f"--env COV_PLATEAU_TIMEOUT={time_plateau}"
        
    cmd = f"""docker run 
            --rm 
            --cpuset-cpus {cpu_id} 
            --name {project}_{driver_name}_X_X_{iteration} 
            --env DRIVER={driver_name} 
            --env DRIVER_FOLDER={driver_folder} 
            --env RESULTS_FOLDER={result_folder} 
            --env TIMEOUT={driver_timeout} 
            --env FORK_MODE=1 
            --env FEEDBACK={feedback_file} 
            {cov_plateau_timeout}
            -v {pwd}:/workspaces/libfuzz 
            --mount type=tmpfs,destination=/tmpfs 
            -t libfuzzpp_fuzzing_{project}"""
            # start_fuzz_driver.sh"""
    # timeout -k 10s $TIMEOUT $FUZZ_BINARY $FUZZ_CORPUS -artifact_prefix=${CRASHES}/ -ignore_crashes=1 -ignore_timeouts=1 -ignore_ooms=1 -detect_leaks=0 -fork=1"
    
    global is_debug
    
    try:
        if is_debug:
            subprocess.run(cmd.split(), check=True)
        else:
            subprocess.run(cmd.split(), check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)        
    except subprocess.CalledProcessError as e:
        if is_debug:
            print(f"Error: Failed to start '{cmd}': {e}")
            
def convert_to_seconds(timeout):
    if timeout.endswith("h"):
        t = int(timeout[:-1]) * 60 *60 
    elif timeout.endswith("m"):
        t = int(timeout[:-1]) * 60
    elif timeout.endswith("s"):
        t = int(timeout[:1])
    else:
        raise Exception(f"I do not know this format {timeout}")
        
    return t

def extract_deep_timeout(base_dir: str, project: str, iteration: str) -> int:
    
    time_budget_path = os.path.join(base_dir, "time_budget.csv")
    with open(time_budget_path, "r") as f:
        for lr in f:
            lar = lr.strip().split("|")
            
            if lar[0] == project and lar[1] == str(iteration):
                return int(lar[2][:-1])
    
    raise Exception(f"{project} {iteration} not found in {time_budget_path}")

def dyn_drv_deep(project, iteration, conf, running_threads = None):
    
    if running_threads is not None:
        cpu_id = -1
        with lock:
            for k in running_threads.keys():
                if running_threads[k] == False:
                    cpu_id = k
                    break
            running_threads[cpu_id] = True
            
        if cpu_id == -1:
            print("ERROR, cpu_id == -1")
            return
    else:
        cpu_id = 0
    
    print(f"Starting {project}-{iteration} on CPU {cpu_id}")
    
    global base_dir
    host_result_folder = os.path.join(base_dir, "workdir_X_X", project, f"iter_{iteration}")
    
    # drivers_for_deep = clst.cluster_drivers(host_result_folder)
    drivers_for_deep = []
    
    print("[INFO] Retrieving the selected drivers")
    with open(os.path.join(host_result_folder, "selected_drivers.txt"), "r") as f:
        for l in f:
            driver_name, _ = l.split(":")
            drivers_for_deep += [driver_name]

    deep_timeout_per_driver = extract_deep_timeout(base_dir, project, iteration)
    
    print("[INFO] Starting in deep fuzzing for the selected drivers")
    for driver_name in drivers_for_deep:
        
        # kick compilation and fuzzing in docker
        kick_fuzzing_camp(project, iteration, driver_name, cpu_id, 
                            driver_timeout = deep_timeout_per_driver, 
                            message = f"DEEP {project} {iteration}")
    
    print(f"[INFO] Terminate fuzzing session for {project}-{iteration}")
    
    if running_threads is not None:
        with lock:
            running_threads[cpu_id] = False
      
def build_container(project):

    global base_dir
    pwd=f"{base_dir}/.."
    
    uid=os.getuid()
    gid=os.getgid()

    cmd = f"""docker build 
            --build-arg USER_UID={uid} --build-arg GROUP_UID={gid} 
            --build-arg target_name={project}
            -t libfuzzpp_fuzzing_{project} --target libfuzzpp_fuzzing 
            -f {pwd}/Dockerfile {pwd}"""
            
    # print(cmd)
    
    try:
        subprocess.run(cmd.split(), check=True, env={"DOCKER_BUILDKIT": "1"})
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to start '{cmd}': {e}")
        exit(1)
    
def init(l):
    global lock
    lock = l
    
def error_callback(exception):
    with open('errors.log', 'a') as f:
        f.write("\n[INFO] A TASK CRASHED!\n")        
        for l in traceback.format_exception(exception):
            f.write(f"{l}\n")
        f.write("\n")

def _main():
    
    parser = argparse.ArgumentParser(description='Automatic Driver Generator')
    parser.add_argument('--debug',  action='store_true', help='Run generation in debug mode')

    args = parser.parse_args()
    
    global is_debug
    is_debug = args.debug

    my_conf = source_bash_file("campaign_configuration.sh")

    projects = my_conf['PROJECTS_STRING'].split(":")
    iterations = range(1, int(my_conf['ITERATIONS']) + 1)

    max_cpu = int(my_conf["MAX_CPUs"])
    
    print("[TODO] Build llvm")
    
    print("[INFO] Pre-Build library containers")
    for p in projects:
        build_container(p)
        
    if is_debug:
        
        for p, i in itertools.product(projects, iterations):
            dyn_drv_deep(p, i, my_conf)
        
    else:
            
        manager = multiprocessing.Manager()
        running_threads = manager.dict()
        lock = multiprocessing.Lock()
        # lock = manager.Lock()

        for c in range(max_cpu):
            running_threads[c] = False
            
        # Create a pool of worker processes
        with multiprocessing.Pool(processes=max_cpu, initializer=init, initargs=(lock,)) as pool:
            
            for p, i in itertools.product(projects, iterations):
                pool.apply_async(func=dyn_drv_deep, args=(p, i, my_conf, running_threads), error_callback=error_callback)
            
            # Close the pool and wait for the work to finish
            pool.close()
            pool.join()

if __name__ == "__main__":
    _main()
