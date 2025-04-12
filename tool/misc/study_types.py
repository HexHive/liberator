#!/usr/bin/env python3

import argparse, tempfile, json, copy, os, re
import clang.cindex


function_declarations = [] # List of AST node objects that are function declarations
type_incomplete = set()    # List of incomplete types
apis_definition = []       # List of APIs with original argument types and extra info (e.g., const)
type_enum = set()

all_types = set()

def get_argument_info(type_str):

    info = {}

    # type is a function pointer
    if "(*)" in type_str:
        info["type_clang"] = type_str
        info["const"] = []
    else:
        # clean any form of [] and *
        n_asterix = type_str.count("*") + type_str.count("[")
        if "[" in type_str:
            # stuffs like char[100] into char*
            type_str = re.sub('\[\d*\]', '*', type_str)
        # type_str = type_str.replace("*","")
        
        
        type_str_token = type_str.strip().replace("*", " * ").split()
        for bad_token in ["enum", "struct"]:
            if bad_token in type_str_token:
                type_str_token.remove(bad_token)
        
        n_const = n_asterix             
        const_pos = [False for _ in range(n_const + 1)]

        print(type_str_token)

        i = 0
        for t in type_str_token:
            if t == "const":
                if i < len(const_pos):
                    const_pos[i] = True
            elif t == "*" and i == 1:
                continue
            else:
                i = i + 1

        while "const" in type_str_token:
            type_str_token.remove("const")
    
        info["type_clang"] = " ".join(type_str_token)
        info["const"] = const_pos

    return info

    # info = {}

    # # type is a function pointer
    # if "(*)" in type_str:
    #     info["type_clang"] = type_str
    #     info["const"] = False
    # else:

    #     # if type_str == "const char *const *":
    #     #     from IPython import embed; embed(); exit(1)

    #     # clean any form of [] and *
    #     n_asterix = type_str.count("*") + type_str.count("[")
    #     if "[" in type_str:
    #         # stuffs like char[100] into char*
    #         type_str = re.sub('\[\d*\]', '', type_str)
    #     type_str = type_str.replace("*","")
        
    #     info["const"] = False
    #     type_str_token = type_str.strip().split(" ")
    #     for bad_token in ["enum", "struct", "const"]:
    #         if bad_token in type_str_token:
    #             type_str_token.remove(bad_token)
    #             if bad_token == "const":
    #                 info["const"] = True

    #     # re-append the * at the end of the type
    #     info["type_clang"] = " ".join(type_str_token) + "*"*n_asterix

    # return info

def _main():

    parser = argparse.ArgumentParser(description='Check types parsing')
    parser.add_argument('-types', '-t', type=str, help='Type folder', required=True)

    args = parser.parse_args()

    types = args.types

    type_files = {}

    for t in os.listdir(types):
        if "alltypes_" not in t:
            continue
        target = t.split("_")[1].split(".")[0]
        t_file = os.path.join(types, t)
        tt = set()
        with open(t_file) as f:
            for l in  f:
                l = l.strip()
                if not l:
                    continue

                i = get_argument_info(l)

                # from IPython import embed; embed(); exit(1)

                tt.add((l, f"{i}"))

        type_files[target] = tt

    for target, tt in type_files.items():
        print("-"*30)
        print(target)
        for s, t in tt:
            if "TIFFFieldInfo" in s:
                print(f"{s} | {t}")

        

if __name__ == "__main__":
    _main()
