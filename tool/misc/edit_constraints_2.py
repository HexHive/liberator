#!/usr/bin/env python3

import argparse
import json

def __main():
    parser = argparse.ArgumentParser(description='Modify library constraints')
    parser.add_argument('-var_len', '-v', type=str, 
                        help='Var_len dependency in the form of "param_X=>param_Y', required=True)
    parser.add_argument('-function', '-f', type=str, 
                        help='Function to work on', required=True)
    parser.add_argument('-constraints', '-c', type=str, help='Constraint File', 
                        required=True)

    args = parser.parse_args()
    
    function    = args.function
    constraints = args.constraints
    var_len     = args.var_len

    print(var_len)

    param_a, param_b = var_len.split("=>")

    constraints_json = None
    with open(constraints, "r") as fd:
        constraints_json = json.load(fd)
        for api in constraints_json:
            if api["function_name"] == function:
                print(f"found: {function}")
                param_x = api[param_a]
                param_x["len_depends_on"] = param_b

    with open(constraints, "w") as fd:
        json.dump(constraints_json, fd)


if __name__ == "__main__":
    __main()