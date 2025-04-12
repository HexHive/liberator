#!/usr/bin/env python3

PROJECT_FOLDER="/workspaces/libfuzz"
import sys, json, os
sys.path.append(PROJECT_FOLDER)

from framework import * 
from driver.ir import Type, PointerType
from common import Utils, DataLayout
from constraints import RunningContext
from dependency import TypeDependencyGraphGenerator
from driver.factory.constraint_based import *
from driver.factory import *

api_info = "/workspaces/libfuzz/analysis/!!LIB!!/work/apipass"
             
libraries = ["cpu_features",
                "libhtp", 
                "libtiff", 
                "libvpx", 
                "minijail", 
                "pthreadpool"]
stats = {}

def add_source(token, source_fun):
    global stats
    s = stats.get(token, {"source": set(), 
        "create": set(), "is_incomplete": False})
    s["source"].add(source_fun)
    stats[token] = s

def add_create(token, create_fun):
    global stats
    s = stats.get(token, {"source": set(), 
        "create": set(), "is_incomplete": False})
    s["create"].add(create_fun)
    stats[token] = s

def is_incomplete(token, is_incomplete):
    global stats
    s = stats.get(token, {"source": set(), 
        "create": set(), "is_incomplete": False})
    s["is_incomplete"] = is_incomplete
    stats[token] = s
    
def _main():
    
    for l in libraries:
        lib_path = api_info.replace("!!LIB!!", l)
        print(lib_path)

        apis_llvm = os.path.join(lib_path, "apis_llvm.json")
        apis_clang = os.path.join(lib_path, "apis_clang.json")
        coerce_map = os.path.join(lib_path, "coerce.log")
        hedader_folder = os.path.join(lib_path, "exported_functions.txt")
        incomplete_types = os.path.join(lib_path, "incomplete_types.txt")
        conditions_file = os.path.join(lib_path, "conditions.json")
        enum_types = os.path.join(lib_path, "enum_types.txt")
        data_layout = os.path.join(lib_path, "data_layout.txt")

        api_list = Utils.get_api_list(apis_llvm, apis_clang, coerce_map, hedader_folder, incomplete_types, "")
        condition = Utils.get_function_conditions(conditions_file, apis_llvm)

        DataLayout.populate(apis_clang, apis_llvm, incomplete_types, 
                            data_layout, enum_types)

        dep_graph = TypeDependencyGraphGenerator(api_list)
        dep_graph = dep_graph.create()
        
        factory = CBFactory(api_list, 1, dep_graph, condition, api_list)

        source_api = set(x for x in factory.get_source_api())

        create_api = set()
        for a in api_list:
            fun_name = a.function_name
            cond = factory.conditions.get_function_conditions(fun_name)
            if RunningContext.is_source(cond.return_at):
                create_api.add(a)

        source_api = [Factory.api_to_apicall(a) for a in source_api]
        create_api = [Factory.api_to_apicall(a) for a in create_api]

        for s in source_api:
            function_name = s.function_name
            rt = s.ret_type
            if isinstance(rt, PointerType):
                rt = rt.get_base_type()
            add_source(rt.token, function_name)
            is_incomplete(rt.token, rt.is_incomplete)

        for c in create_api:
            function_name = c.function_name
            rt = c.ret_type
            if isinstance(rt, PointerType):
                rt = rt.get_base_type()
            add_create(rt.token, function_name)
            is_incomplete(rt.token, rt.is_incomplete)

        # add_source(token, create_fun)
        # is_incomplete(token, is_incomplete)

    for t, s in stats.items():
        str_incomplete = "complete"
        if s["is_incomplete"]:
            str_incomplete = "incomplete"
        print(f"{t} -- {str_incomplete}")
        print(f"source: {s['source']}")
        print(f"create: {s['create']}")
    
if __name__ == "__main__":
    _main()