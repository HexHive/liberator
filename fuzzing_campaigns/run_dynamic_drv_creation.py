#!/usr/bin/python3

import subprocess, itertools, os, sys, multiprocessing, argparse, traceback, shutil
from datetime import datetime
import numpy as np
from sklearn.cluster import AffinityPropagation
from Levenshtein import distance as levenshtein_distance

from typing import Set, Tuple

global base_dir
base_dir = os.getcwd()
PROJECT_FOLDER=f"{base_dir}/.."
sys.path.append(PROJECT_FOLDER)
from framework import * 
from generator import Generator, Configuration
from framework.driver.factory.constraint_based_grammar import ApiSeqState
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
    "libucl": 126,
    "libdwarf": 334,
    "libplist": 101,
    "libsndfile": 34,
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

def create_driver_generator_conf(project, iteration, config):
    
    policy = config["POLICY"]
    
    global base_dir    
    generator_conf_path = os.path.join(base_dir, f"generator_{project}_{iteration}.toml")    
    
    working_dir = os.path.join(base_dir, "workdir_X_X", project, f"iter_{iteration}")
    an_res_dir = os.path.join(base_dir, "..", "analysis", project, "work", "apipass")
    an_inc_dir = os.path.join(base_dir, "..", "analysis", project, "work", "include")
    pub_head_dir = os.path.join(base_dir, "..", "targets", project)
    
    driver_size = config["NUM_OF_API_GRAMMAR"]
    num_unknown_api = config["NUM_OF_UNKNOWN_API"]
    bias = config["BIAS"]
    
    with open(generator_conf_path, "w") as f:
        
        f.write("[analysis]\n")
        f.write(f"apis_llvm = \"{an_res_dir}/apis_llvm.json\"\n")
        f.write(f"apis_clang = \"{an_res_dir}/apis_clang.json\"\n")
        f.write(f"coercemap = \"{an_res_dir}/coerce.log\"\n")
        f.write(f"headers = \"{an_res_dir}/exported_functions.txt\"\n")
        f.write(f"incomplete_types = \"{an_res_dir}/incomplete_types.txt\"\n")
        f.write(f"conditions = \"{an_res_dir}/conditions.json\"\n")
        
        if config["USE_CUSTOM_APIS"] == "1":
            custom_api_path = os.path.join(base_dir, "..",  "targets", project, "custom_apis_minized.txt")
            f.write(f"minimum_apis = \"{custom_api_path}\"\n")
        else:
            f.write(f"minimum_apis = \"\"\n")
            
        f.write(f"data_layout = \"{an_res_dir}/data_layout.txt\"\n")
        f.write(f"enum_types = \"{an_res_dir}/enum_types.txt\"\n")
        f.write(f"weights = \"{an_res_dir}/weights.json\"\n")
        f.write("\n")
        
        f.write("[generator]\n")
        f.write(f"workdir = \"{working_dir}\"\n")
        f.write(f"policy = \"{policy}\"\n")
        f.write(f"dep_graph = \"type\"\n")
        f.write("pool_size = 1\n")
        f.write(f"driver_size = {driver_size}\n")
        f.write(f"num_unknown_api = {num_unknown_api}\n")
        f.write("num_seeds = 1\n")
        f.write("backend = \"libfuzz\"\n")
        f.write(f"bias = \"{bias}\"\n")
        
        f.write("\n")
        
        f.write("[backend]\n")
        f.write(f"headers = \"{an_inc_dir}\"\n")
        f.write(f"public_headers = \"{pub_head_dir}/public_headers.txt\"\n")
        f.write("\n")
        
    return generator_conf_path

def get_new_driver(sess, drivers_list, driver_list_history):
    
    max_trial = 10
    while max_trial > 0:
        driver = sess._factory.create_random_driver()
        apichain = driver.statements_apicall
        apichain_str = ";".join([str(l.function_name) for l, _ in apichain])
        if apichain_str in driver_list_history:
            max_trial -= 1
            continue            
        else:
            break

    driver_list_history.add(apichain_str)
    driver_name = sess._backend.get_name()

    print(f"Storing driver: {driver_name}") 
    sess._backend.emit_driver(driver, driver_name)

    print(f"Storing seeds for: {driver_name}")
    sess._backend.emit_seeds(driver, driver_name)

    print(f"Storing metadata for {driver_name}:")
    sess.dump_metadata(driver, driver_name)

    if driver_name.endswith(".cc"):
        driver_name = driver_name[:-3]
        
    if hasattr(driver, "statements_apicall"):
        drivers_list[driver_name] = (driver.statements_apicall, ApiSeqState.UNKNOWN, 0)
    else:
        drivers_list[driver_name] = (driver, ApiSeqState.NEGATIVE, 0)

    return driver_name

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
    
def push_feedfback(sess, result_folder, driver_name, time, cause, 
                   time_plateau, drivers_list, n_seeds):
    
    global base_dir
    
    try:        
        time_plateau = int(time_plateau)
    except:
        time_plateau = 0
        
    try:
        time = int(time)
    except:
        time = 0
        
    if cause == "":
        cause = "C"
            
    with open(f"{result_folder}/feedback_received.txt", "a") as f:
        f.write(f"{driver_name}|{time}|{cause}|{n_seeds}\n")
        
    driver, _, _ = drivers_list[driver_name]
       
    api_cause = ApiSeqState.NEGATIVE
    if cause == "I":
        api_cause = ApiSeqState.POSITIVE

    if ((cause == "O" or cause == "P") and 
        time > time_plateau):
        api_cause = ApiSeqState.POSITIVE
        
    # this is a special case when the only seed is empty
    if n_seeds == 1 and len(driver) == 1:
        api_cause = ApiSeqState.POSITIVE

    update_api_state = getattr(sess._factory, "update_api_state", None)
    if update_api_state is not None and callable(update_api_state):
        api_state = sess._factory.update_api_state(driver, api_cause, n_seeds)
        drivers_list[driver_name] = (driver, api_state, n_seeds)
        
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

def seed_is_empty(project, driver_name, iteration):
    
    global base_dir
    seed_path = os.path.join(base_dir, "workdir_X_X", project, 
                                 f"iter_{iteration}", "corpus_new", driver_name, "seed1.bin")
    
    return os.path.getsize(seed_path) == 0

def get_produced_seed(project, driver_name, iteration):     
    global base_dir
    corpus_folder = os.path.join(base_dir, "workdir_X_X", project, f"iter_{iteration}", "corpus_new", driver_name)
    
    items = os.listdir(corpus_folder)
    files = [f for f in items if os.path.isfile(os.path.join(corpus_folder, f))]
    n_seeds = len(files)
    
    return n_seeds

def dyn_drv_gen(project, iteration, conf, running_threads = None):
    
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
    
    time_plateau = "30" # seconds
    
    # prepare generator.toml
    config_file = create_driver_generator_conf(project, iteration, conf)
    
    # load driver generator
    config = Configuration(config_file)
    # very dangerous :) but it should be ok here
    _ = config.work_dir
    sess = Generator(config)
    drivers_list = dict()
    library_api_used = set()
    driver_list_history = set()
    
    # from IPython import embed; embed(); exit()
    
    is_api_perc_upperbound = "API_PERC_UPPERBOUND" in conf 
    if is_api_perc_upperbound:
        
        api_perc_max = int(conf["API_PERC_UPPERBOUND"])
        
        if "DEEP_TIMEOUT" not in conf:
            raise("env var DEEP_TIMEOUT and API_PERC_UPPERBOUND must be set together")
        
    deep_timeout = None
    if "DEEP_TIMEOUT" in conf:        
        deep_timeout = convert_to_seconds(conf['DEEP_TIMEOUT'])
    
    whole_timeout = convert_to_seconds(conf['TIMEOUT'])
    
    start_time = datetime.now()
    
    global base_dir
    host_result_folder = os.path.join(base_dir, "workdir_X_X", project, f"iter_{iteration}")
    
    tot_api_project = tot_api[project]

    i = 0
    while True:
        
        current_time = datetime.now()
        if (current_time - start_time).total_seconds() >= whole_timeout:
            break

        l_used = len(library_api_used)
        perc_used = (l_used/tot_api_project)*100
        print(f"[INFO] {l_used}/{tot_api_project} [{perc_used}%] API funcs used")
        if is_api_perc_upperbound and perc_used >= api_perc_max:
            print("[INFO] Enough API func")
            break
    
        # get a new driver
        driver_name = get_new_driver(sess, drivers_list, driver_list_history)
        
        # clean feedback on the host
        feedback_file = os.path.join(host_result_folder, "feedback.txt")
    
        if os.path.exists(feedback_file):
            os.remove(feedback_file)    
            
        # kick compilation and fuzzing in docker
        kick_fuzzing_camp(project, iteration, driver_name, 
                            cpu_id, time_plateau, message = "GEN")
        
        # process feedback
        if os.path.exists(feedback_file):
            with open(feedback_file, "r") as f:
                cause_driver_stop = f.readline()[:-1]
                driver_exec_time = f.readline()[:-1]
                
            n_seeds = get_produced_seed(project, driver_name, iteration)
            # has_empty_seed = seed_is_empty(project, driver_name, iteration)
                
            push_feedfback(sess, host_result_folder, driver_name, driver_exec_time, 
                        cause_driver_stop, time_plateau, drivers_list, n_seeds)
            
            # to save some space, I delete the drivers that do not contribute to new coverage
            if len(os.listdir(os.path.join(host_result_folder, "corpus_new", driver_name))) == 1:
                try:
                    os.remove(os.path.join(host_result_folder, "drivers", driver_name))
                    os.remove(os.path.join(host_result_folder, "profiles", f"{driver_name}_profile"))
                    os.remove(os.path.join(host_result_folder, "cluster_drivers", f"{driver_name}_cluster"))
                except:
                    pass
            # I count its APIs only if the driver 'seems' good
            else:
                # print("BBBBB")
                # from IPython import embed; embed(); exit(1)
                last_driver = drivers_list[driver_name]
                for api_func in last_driver[0]:
                    library_api_used.add(api_func[0].function_name)
                    
        with open(os.path.join(base_dir, f"perc_api_{project}.txt"), "w") as f:
            f.write(f"total: {tot_api_project}\n")
            f.write(f"used: {l_used}\n")
    
    print("[INFO] Storing paths observed")
    with open(os.path.join(host_result_folder, "paths_observed.txt"), "w") as file:
        for d, (l, t, s) in drivers_list.items():
            x = ";".join([str(l.function_name) for l, _ in l])
            file.write(f"{d}:{x}:{t}:{s}\n")
            
    # mv the generator.toml file in the workdir folder
    config_file_name = os.path.basename(config_file)
    os.rename(config_file, os.path.join(host_result_folder, config_file_name))
    
    if deep_timeout is not None:
        start_time = datetime.now()
        
        drivers_for_deep = clst.cluster_drivers(host_result_folder)
        
        print("[INFO] Storing the selected drivers")
        with open(os.path.join(host_result_folder, "selected_drivers.txt"), "w") as f:
            for driver_name, api_seq in drivers_for_deep:
                f.write(f"{driver_name}:{api_seq}\n")
        
        deep_timeout_per_driver = f"{int(deep_timeout/len(drivers_for_deep))}s"
        
        print("[INFO] Starting in deep fuzzing for the selected drivers")
        for driver_name, _ in drivers_for_deep:

            # cp corpus for driver
            x = os.path.join(host_result_folder, "corpus")
            y = os.path.join(host_result_folder, "corpus_new", driver_name)
            z = os.path.join(host_result_folder, "corpus", driver_name)
            os.system(f"rm -R {z}")
            os.system(f"cp -r {y} {x}")
            
            # kick compilation and fuzzing in docker
            kick_fuzzing_camp(project, iteration, driver_name, cpu_id, 
                              driver_timeout = deep_timeout_per_driver, message = "DEEP")
            
    
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
            dyn_drv_gen(p, i, my_conf)
        
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
                pool.apply_async(func=dyn_drv_gen, args=(p, i, my_conf, running_threads), error_callback=error_callback)
            
            # Close the pool and wait for the work to finish
            pool.close()
            pool.join()

if __name__ == "__main__":
    _main()
