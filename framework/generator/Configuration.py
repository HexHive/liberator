from functools import cached_property

import os, json
from os import path
import tomli, shutil

from typing import Dict, List, Optional, Set, Tuple

from dependency import TypeDependencyGraphGenerator
from dependency import UndefDependencyGraphGenerator
from grammar import GrammarGenerator, NonTerminal, Terminal

from constraints import ConditionManager

from backend import BackendDriver, MockBackendDriver, LFBackendDriver
from common import Utils, DataLayout

from driver.factory.only_type import *
from driver.factory.constraint_based import *
from driver.factory.constraint_based_search import *
from driver.factory.constraint_based_grammar import *
from driver.factory.constraint_based_backward import *

from bias import Bias, WBias, SBias, IBias, FBias

from generator import Pool

class Configuration:
    def __init__(self, config_path, overwrite_path = None):
        
        if not path.isfile(config_path):
            raise Exception(f"The configuration {config_path} is not valid")

        with open(config_path, "rb") as f:
            self._config = tomli.load(f)

        if overwrite_path is not None:
            print(f"[INFO] Found {overwrite_path}, overwriting some parameters")
            with open(overwrite_path, "rb") as f:
                new_conf = tomli.load(f)

                # overwrite (section, parameter) with overwrite_path values
                for k_section, v in new_conf.items():
                    if k_section in self._config:
                        for k_par, v_par in v.items():
                            self._config[k_section][k_par] = v_par

        self.start_term = NonTerminal("start")
        self.end_term = Terminal("end")

        self._config_path = config_path
        self._overwrite_path = overwrite_path

    def get_info(self):
        if self._overwrite_path is not None:
            return f"{self._config_path}({self._overwrite_path})"
    
        return f"{self._config_path}"

    @cached_property
    def bias(self):
        
        if not "generator" in self._config:
            raise Exception("'generator' not defined")

        generator = self._config["generator"]

        # default value
        if not "bias" in generator:
            raise Exception("'bias' not defined")
        
        bias_type = generator["bias"]
        
        # "none" return the default bias class
        if bias_type == "none":
            return Bias()
        
        if bias_type == "api_frequency":
            return WBias(self.dependency_graph)
        
        if bias_type == "seed_number":
            return SBias()

        if bias_type == "field_inter":
            return IBias(self.function_conditions)
        
        if bias_type == "field_sum":
            return FBias(self.function_conditions)
        
        raise NotImplementedError

    @cached_property
    def driver_size(self):

        if not "generator" in self._config:
            raise Exception("'generator' not defined")

        generator = self._config["generator"]

        # default value
        if not "driver_size" in generator:
            return 10

        return generator["driver_size"]

    @cached_property
    def work_dir(self):
        wd = self._config["generator"]["workdir"]
        shutil.rmtree(wd, ignore_errors=True)
        os.makedirs(wd, exist_ok=True)
        return wd

    @cached_property
    def queue_dir(self):
        d = os.path.join(self.work_dir, "queue")
        os.makedirs(d, exist_ok=True)
        return d

    @cached_property
    def target_library(self):
        if not "generator" in self._config:
            raise Exception("'fuzzer' not defined")

        generator = self._config["generator"]

        # default value
        if not "target_library" in generator:
            raise Exception("'target_library' not defined")

        return generator["target_library"]

    @cached_property
    def cache_dir(self):
        d = os.path.join(self.work_dir, "cache")
        os.makedirs(d, exist_ok=True)
        return d

    @cached_property
    def drivers_dir(self):
        d = os.path.join(self.work_dir, "drivers")
        os.makedirs(d, exist_ok=True)
        return d
    
    @cached_property
    def metadata_dir(self):
        d = os.path.join(self.work_dir, "metadata")
        os.makedirs(d, exist_ok=True)
        return d

    @cached_property
    def seeds_dir(self):
        d = os.path.join(self.work_dir, "corpus")
        os.makedirs(d, exist_ok=True)
        return d

    @cached_property
    def headers_dir(self):
        if not "backend" in self._config:
            raise Exception("'backend' not defined")

        backend = self._config["backend"]

        if not "headers" in backend:
            raise Exception("'headers' not defined")

        return backend["headers"]
    
    @cached_property
    def public_headers(self):
        if not "backend" in self._config:
            raise Exception("'backend' not defined")

        backend = self._config["backend"]

        if not "public_headers" in backend:
            raise Exception("'public_headers' not defined")

        return backend["public_headers"]

    @cached_property
    def reports_dir(self):
        d = os.path.join(self.work_dir, "reports")
        os.makedirs(d, exist_ok=True)
        return d

    @cached_property
    def api_list_all(self):

        if not "analysis" in self._config:
            raise Exception("'analysis' not defined")

        analysis = self._config["analysis"]

        if not "apis_llvm" in analysis:
            raise Exception("'apis_llvm' not defined")

        if not "apis_clang" in analysis:
            raise Exception("'apis_clang' not defined")
        
        if not "headers" in analysis:
            raise Exception("'headers' not defined")

        if not "coercemap" in analysis:
            raise Exception("'coercemap' not defined")
        
        apis_llvm = analysis["apis_llvm"]
        apis_clang = analysis["apis_clang"]
        hedader_folder = analysis["headers"]
        coerce_map = analysis["coercemap"]
        incomplete_types = analysis["incomplete_types"]

        return Utils.get_api_list(apis_llvm, apis_clang, coerce_map, hedader_folder, incomplete_types, "")

    @cached_property
    def api_list(self):

        if not "analysis" in self._config:
            raise Exception("'analysis' not defined")

        analysis = self._config["analysis"]

        if not "apis_llvm" in analysis:
            raise Exception("'apis_llvm' not defined")

        if not "apis_clang" in analysis:
            raise Exception("'apis_clang' not defined")
        
        if not "headers" in analysis:
            raise Exception("'headers' not defined")

        if not "coercemap" in analysis:
            raise Exception("'coercemap' not defined")

        if not "minimum_apis" in analysis:
            raise Exception("'minimum_apis' not defined")

        apis_llvm = analysis["apis_llvm"]
        apis_clang = analysis["apis_clang"]
        hedader_folder = analysis["headers"]
        coerce_map = analysis["coercemap"]
        incomplete_types = analysis["incomplete_types"]
        minimum_apis = analysis["minimum_apis"]

        return Utils.get_api_list(apis_llvm, apis_clang, coerce_map, hedader_folder, incomplete_types, minimum_apis)

    # this builds a static structure in DataLayout
    def build_data_layout(self):
        if not "analysis" in self._config:
            raise Exception("'analysis' not defined")

        analysis = self._config["analysis"]

        if not "apis_llvm" in analysis:
            raise Exception("'apis_llvm' not defined")

        if not "apis_clang" in analysis:
            raise Exception("'apis_clang' not defined")

        if not "incomplete_types" in analysis:
            raise Exception("'incomplete_types' not defined")

        if not "data_layout" in analysis:
            raise Exception("'data_layout' not defined")
        
        if not "enum_types" in analysis:
            raise Exception("'enum_types' not defined")
        
        apis_llvm = analysis["apis_llvm"]
        apis_clang = analysis["apis_clang"]
        incomplete_types = analysis["incomplete_types"]
        data_layout = analysis["data_layout"]
        enum_types = analysis["enum_types"]

        data_layout_inst = DataLayout.instance()
        data_layout_inst.setup(apis_clang, apis_llvm, incomplete_types, 
                               data_layout, enum_types)

    def build_condition_manager(self):
        cond_manager = ConditionManager.instance()
        cond_manager.setup(self.api_list, self.api_list_all,
                           self.function_conditions)

    @cached_property
    def dependency_graph(self):

        if not "generator" in self._config:
            raise Exception("'generator' not defined")

        generator = self._config["generator"]

        if not "dep_graph" in generator:
            raise Exception("'dep_graph' not defined")

        dep_graph_policy = generator["dep_graph"]

        if dep_graph_policy == "type":
            TDGG = TypeDependencyGraphGenerator(self.api_list)
            dep_graph = TDGG.create()
        elif dep_graph_policy == "undef":
            UDGG = UndefDependencyGraphGenerator(self.api_list)
            dep_graph = UDGG.create()

        return dep_graph


    @cached_property
    def factory(self):

        if not "generator" in self._config:
            raise Exception("'generator' not defined")

        generator = self._config["generator"]

        if not "policy" in generator:
            raise Exception("'policy' not defined")

        policy = generator["policy"]

        if policy == "only_type":
            dep_graph = self.dependency_graph
            GG = GrammarGenerator(self.start_term, self.end_term)
            InitGrammar = GG.create(dep_graph)
            
            # InitGrammar.pprint()

            return OTFactory(self.api_list, self.driver_size, InitGrammar)

        if policy == "constraint_based":
            dep_graph = self.dependency_graph
            return CBFactory(self.api_list, self.driver_size, dep_graph, 
                             self.function_conditions, self.bias)
            
        if policy == "constraint_based_grammar":
            dep_graph = self.dependency_graph
            return CBGFactory(self.api_list, self.driver_size, dep_graph, 
                              self.function_conditions, self.bias,
                              self.number_of_unknown)

        if policy == "constraint_based_search":
            dep_graph = self.dependency_graph
            # pool_size = self.pool.pool_size
            return CBSFactory(self.api_list, self.driver_size, dep_graph, 
                              self.function_conditions, self.weights)

        if policy == "constraint_based_backward":
            dep_graph = self.dependency_graph
            return CBBFactory(self.api_list, self.driver_size, dep_graph, 
                              self.function_conditions)

        raise NotImplementedError
    
    @cached_property
    def number_of_unknown(self):
        if not "generator" in self._config:
            raise Exception("'generator' not defined")

        generator = self._config["generator"]

        if not "num_unknown_api" in generator:
            raise Exception("'num_unknown_api' not defined")

        num_unknown_api = generator["num_unknown_api"]
        
        return int(num_unknown_api)

    @cached_property
    def function_conditions(self):
        if not "analysis" in self._config:
            raise Exception("'analysis' not defined")

        analysis = self._config["analysis"]

        if not "conditions" in analysis:
            raise Exception("'conditions' not defined")
        
        if not "apis_llvm" in analysis:
            raise Exception("'apis_llvm' not defined")

        conditions_file = analysis["conditions"]
        apis_llvm = analysis["apis_llvm"]
        
        return Utils.prase_function_conditions(conditions_file, apis_llvm)
        
    @cached_property
    def num_seeds(self):
        if not "generator" in self._config:
            raise Exception("'generator' not defined")

        generator = self._config["generator"]

        if not "num_seeds" in generator:
            raise Exception("'num_seeds' not defined")

        return int(generator["num_seeds"])

    @cached_property
    def backend(self) -> BackendDriver:
        if not "generator" in self._config:
            raise Exception("'generator' not defined")

        generator = self._config["generator"]

        if not "backend" in generator:
            raise Exception("'backend_driver' not defined")

        backend = generator["backend"]
        
        if backend == "mock":
            return MockBackendDriver(self.drivers_dir, self.seeds_dir, self.num_seeds)

        if backend == "libfuzz":
            return LFBackendDriver(self.drivers_dir, self.seeds_dir, self.num_seeds, self.headers_dir, self.public_headers)

        raise NotImplementedError

    @cached_property
    def pool(self) -> Pool:
        if not "generator" in self._config:
            raise Exception("'generator' not defined")

        fuzzer = self._config["generator"]

        if not "pool_size" in fuzzer:
            raise Exception("'pool_size' not defined")

        pool_size = fuzzer["pool_size"]

        return Pool(pool_size)


    @cached_property
    def weights(self) -> Dict[str,int]:
        if not "analysis" in self._config:
            raise Exception("'analysis' not defined")

        analysis = self._config["analysis"]

        if not "weights" in analysis:
            raise Exception("'weights' not defined")

        weights_file = analysis["weights"]

        with open(weights_file) as  f:
            ws = json.load(f)

        return ws
        