#!/usr/bin/env python3

PROJECT_FOLDER="/workspaces/libfuzz"

import sys
sys.path.append(PROJECT_FOLDER)

import argparse
from framework import * 
from generator import Generator, Configuration
import logging

logging.getLogger().setLevel(logging.WARN)
logging.getLogger("generator").setLevel(logging.DEBUG)


def __main():

    # default_config = "./targets/simple_connection/fuzz.toml"
    default_config = PROJECT_FOLDER + "/targets/libtiff/generator.toml"

    parser = argparse.ArgumentParser(description='Automatic Driver Generator')
    parser.add_argument('--config', type=str, help='The configuration', default=default_config)

    args = parser.parse_args()

    config = Configuration(args.config)
    
    fcs = config.function_conditions

    from IPython import embed; embed();

    print(fcs)

if __name__ == "__main__":
    __main()

