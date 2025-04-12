#!/usr/bin/env python3

PROJECT_FOLDER="/workspaces/libfuzz"

from flask import Flask, request
import threading

import sys
sys.path.append(PROJECT_FOLDER)

app = Flask(__name__)

import argparse
from framework import * 
from generator import Generator, Configuration
from framework.driver.factory.constraint_based_grammar import ApiSeqState
import html
import logging

# Shared counter variable
# not sure I need that
lock = threading.Lock()  # Lock to ensure thread safety
sess = None
drivers_list = dict()
result_folder = ""

@app.route('/')
def index():
    if sess is None:
        return "Session not loaded. Check configuration."
    else:
        config_info = sess._config.get_info()
        s = f"Session loaded w/: {config_info}<br />\n"

        factory_str = html.escape(str(sess._factory))
        s += f"Factory: {factory_str} <br />\n"

        s += f"Drivers generated: {len(drivers_list)}<br />\n"
        for d, (l, t) in drivers_list.items():
            x = ";".join([str(l.function_name) for l, _ in l])
            s += f"{d}: {x} [{t}]<br />\n"
        
        return s

@app.route('/get_new_driver')
def get_new_driver():

    driver = sess._factory.create_random_driver()
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
        drivers_list[driver_name] = (driver.statements_apicall, ApiSeqState.UNKNOWN)
    else:
        drivers_list[driver_name] = (driver, ApiSeqState.UNKNOWN)

    return driver_name

@app.route('/push_feedback')
def push_feedback():
    driver_name = request.args.get('driver', '')
    if driver_name == '':
        return "Error: no driver name"
    
    time = request.args.get('time', -1, type=int)
    if time == -1:
        return "Error: time not given"

    time_plateau = request.args.get('time_plateau', -1, type=int)
    if time_plateau == -1:
        return "Error: time_plateau not given"

    cause = request.args.get('cause', '')
    if cause == -1:
        return "Error: cause not given"

    with open(f"{result_folder}/feedback_received.txt", "a") as f:
        f.write(f"{driver_name}|{time}|{cause}\n")
       
    api_cause = ApiSeqState.NEGATIVE
    if cause == "I":
        api_cause = ApiSeqState.POSITIVE

    if ((cause == "O" or cause == "P") and 
        time > time_plateau):
        api_cause = ApiSeqState.POSITIVE
    
    # I am not sure the factory implements the method "update_api_state"
    update_api_state = getattr(sess._factory, "update_api_state", None)
    if update_api_state is not None and callable(update_api_state):
        driver, _ = drivers_list[driver_name]
        api_state = sess._factory.update_api_state(driver, api_cause)
        drivers_list[driver_name] = (driver, api_state)
        return "ok"
    else:
        return "error: factory {sess._factory} does not have \"update_api_state\" method"

if __name__ == '__main__':

    # default_config = PROJECT_FOLDER + "/regression_tests/condition_extractor/test_simpleapi/generator.toml"
    # default_config = PROJECT_FOLDER + "/regression_tests/condition_extractor/test_full/generator.toml"
    # default_config = PROJECT_FOLDER + "/targets/uriparser/generator.toml"
    # default_config = PROJECT_FOLDER + "/targets/libhtp/generator.toml"
    default_config = PROJECT_FOLDER + "/targets/libtiff/generator.toml"
    # default_config = PROJECT_FOLDER + "/targets/cpu_features/generator.toml"
    # default_config = PROJECT_FOLDER + "/targets/minijail/generator.toml"
    # default_config = PROJECT_FOLDER + "/targets/libvpx/generator.toml"
    # default_config = PROJECT_FOLDER + "/targets/pthreadpool/generator.toml"
    # default_config = PROJECT_FOLDER + "/targets/libaom/generator.toml"
    # default_config = PROJECT_FOLDER + "/targets/libpcap/generator.toml"
    # default_config = PROJECT_FOLDER + "/targets/c-ares/generator.toml"
    # default_config = PROJECT_FOLDER + "/targets/cjson/generator.toml"
    # default_config = PROJECT_FOLDER + "/targets/zlib/generator.toml"

    parser = argparse.ArgumentParser(description='Automatic Driver Generator')
    parser.add_argument('--config', type=str, help='The configuration', default=default_config)

    parser.add_argument('--overwrite', type=str, help='Set of parameters that overwrite the `config` toml file. Used to standardize configuration when testing multipe libraries.')

    args = parser.parse_args()

    config = Configuration(args.config, args.overwrite)

    # very dangerous :) but it should be ok here
    result_folder = config.work_dir

    sess = Generator(config)

    app.run(host="0.0.0.0", debug=True)
