#!/usr/bin/env python3

import argparse
import json

def __main():
    parser = argparse.ArgumentParser(description='Modify library constraints')
    parser.add_argument('-new', '-n', type=str, 
                        help='New constraint to add', required=True)
    parser.add_argument('-function', '-f', type=str, 
                        help='Function to work on', required=True)
    parser.add_argument('-argument', '-a', type=int, 
                        help='Argument to work on (-1 for return value)', 
                        required=True)
    parser.add_argument('-constraints', '-c', type=str, help='Constraint File', 
                        required=True)

    args = parser.parse_args()
    
    new_const   = args.new
    function    = args.function
    argument    = args.argument
    constraints = args.constraints

    print(new_const)

    new_const_json = None
    with open(new_const, "r") as fd:
        new_const_json = json.load(fd)
    
    print(new_const_json)

    constraints_json = None
    with open(constraints, "r") as fd:
        constraints_json = json.load(fd)
        for api in constraints_json:
            if api["function_name"] == function:
                print(f"found: {function}")
                param_x = None
                if argument == -1:
                    param_x = api["return"]
                else:
                    param_x = api[f"param_{argument}"]

                param_x["access_type_set"] += [new_const_json]

    with open(constraints, "w") as fd:
        json.dump(constraints_json, fd)


if __name__ == "__main__":
    __main()