import copy
import random
from typing import Dict, List, Optional, Set, Tuple

import networkx as nx

from common import Api, FunctionConditionsSet
from constraints import RunningContext, ConditionManager
from dependency import DependencyGraph
from driver import Driver
from driver.factory.constraint_based import CBFactory
from driver.factory import Factory, EmptyDriverSpace
from driver.ir import PointerType, Variable, AllocType
from driver.ir import NullConstant, AssertNull, SetNull, Address, Variable

class CBSFactory(CBFactory):
    api_list            : Set[Api]
    driver_size         : int
    conditions          : FunctionConditionsSet
    dependency_graph    : Dict[Api, Set[Api]]
    condition_manager   : ConditionManager

    MAX_ALLOC_SIZE = 1024
    
    def __init__(self, api_list: Set[Api], driver_size: int, 
                    dgraph: DependencyGraph, conditions: FunctionConditionsSet, weights: Dict[str,int]):
        self.api_list = api_list
        self.driver_size = driver_size
        # self.dependency_graph = dgraph
        self.conditions = conditions

        api_list_name = [a.function_name for a in self.api_list]

        # I need this to build synthetic constraints in "update" method
        RunningContext.type_to_hash = {}
        for f, c in self.conditions:
            for arg in c.argument_at + [c.return_at]:
                for at in arg.ats:
                    RunningContext.type_to_hash[at.type_string] = at.type

        # DependencyGraph must be inverted, this is an "error". It probably
        # needs refactor in the future
        inv_dep_graph = dict((k, set()) for k in list(dgraph.keys()))
        for api, deps in dgraph.items():
            for dep in deps:
                if not dep in inv_dep_graph:
                    inv_dep_graph[dep] = set()
                
                inv_dep_graph[dep].add(api)
        self.dependency_graph = inv_dep_graph

        self.condition_manager = ConditionManager.instance()

        self.source_api = list(self.condition_manager.get_source_api())
        self.init_api = list(self.condition_manager.get_init_api())
        self.sink_api = list(self.condition_manager.get_sink_api())

        G = nx.DiGraph()

        for api, adj_api in self.dependency_graph.items():
            weight = 0
            function_name = api.function_name
            if function_name in weights:
                weight = weights[function_name]

            G.add_node(api, weight = weight)

            no_loop = api in self.source_api + self.init_api + self.sink_api
            
            if api in self.sink_api:
                continue

            for api_n in adj_api:
                if api_n in self.source_api:
                    continue
            
                if api not in self.source_api:
                    if api_n in self.init_api:
                        continue

                if no_loop and api_n == api:
                    continue

                G.add_edge(api, api_n)

        self.G = G

        self.possible_driver_pool = {}

        weights_sorted = sorted(weights.items(), key=lambda x:x[1], 
                                    reverse=True)

        self.weights = weights_sorted[:5]

        self.driver_generator = self.get_next_driver()

        # LIBAOM TESTS
        # target_final = "aom_codec_decode"
        # target_final = "aom_codec_get_frame"

        # LIBVPX TEST
        # target_final = "vpx_codec_decode"
        # target_final = "vpx_codec_get_frame"
        # target_final = "vpx_codec_control_"

        # LIBHTP TEST
        # target_final = "htp_connp_res_data_consumed"

        distinct_apis = set()

        for t_name, _ in self.weights:
            target = self.get_api(t_name)

            exit_all = False

            for source in self.source_api:
                try:
                    # for path in nx.all_simple_paths(self.G, 
                    #                             source=source, 
                    #                             target=target, 
                    #                             cutoff=5):
                    for path in nx.all_shortest_paths(self.G, 
                                                source=source, 
                                                target=target):
                        
                        a_chain = self.try_to_instantiate_chain(path)
                        if a_chain == {}:
                            continue    
                    
                        for n in path:
                            distinct_apis.add(n)
                        
                            # if len(distinct_apis) >= 20:
                            #     exit_all = True
                            #     break

                        if exit_all:
                            break
                except:
                    continue

                if exit_all:
                    break

        import os
        target = os.environ["TARGET"].split("/")[-1]
        print(f"[INFO] TARGET: {target}")
        with open(f"{target}_cbsfactory.txt", "w") as f:
            for a in distinct_apis:
                fun_name = a.function_name
                f.write(fun_name + "\n")

        # print("CBSFactory -- test dio cane")
        # from IPython import embed; embed(); exit(1)
        exit(1)

    attempt = 3

    def get_api(self, function_name):
        all_function_name = [a.function_name for a in
                             self.dependency_graph.keys()]

        if function_name not in all_function_name:
            return None
        
        xx = [a for a in self.dependency_graph.keys() 
              if a.function_name == function_name]

        return xx[0]
    
    def try_to_instantiate_chain(self, chain):

        rng_ctx = RunningContext()

        get_cond = lambda x: self.conditions.get_function_conditions(x.function_name)
        to_api = lambda x: Factory.api_to_apicall(x)

        inst_chain = []

        for api in chain:
                    
            api_condition = get_cond(api)
            api_call = to_api(api)

            rng_ctx, unsat_var_2 = self.try_to_instantiate_api_call(api_call, api_condition, rng_ctx)      # type: ignore

            l_unsat_var = len(unsat_var_2)
            if l_unsat_var == 0:
                inst_chain += [api_call]
            else:
                return {}
            
        return (inst_chain, rng_ctx)
    

    # target_list = ["foo", "bar", "zoo"]
    # source_list = ["s1", "s2"]

    # def generate_paths(source, target):
    #     for i in range(1, 10):
    #         # return f"path {i} from {source} to {target}"
    #         yield f"path {i} from {source} to {target}"

    # def next_driver():  

    #     for target in target_list:
    #         for source in source_list:
    #             g = generate_paths(source, target)
    #             for p in g:
    #                 yield p


    def get_next_driver(self):
        for t_name, _ in self.weights:
            target = self.get_api(t_name)

            for source in self.source_api:

                try:
                    for path in nx.all_simple_paths(self.G, 
                                                source=source, 
                                                target=target, 
                                                cutoff=self.driver_size):
                    
                        a_chain = self.try_to_instantiate_chain(path)
                        if a_chain == {}:
                            continue

                        yield a_chain
                except:
                    continue

        raise EmptyDriverSpace()

    def create_random_driver(self) -> Driver:

        drv, context = next(self.driver_generator)

        statements_apicall = []
        for api_call in drv:
            statements_apicall += [api_call]
            if (isinstance(api_call.ret_type, PointerType) and
                not isinstance(api_call.ret_var, NullConstant)):
                var = api_call.ret_var.get_variable()
                statements_apicall += [AssertNull(var.get_buffer())]
            # sink APIs have only 1 argument
            if self.condition_manager.is_sink(api_call):
                arg = api_call.arg_vars[0]
                if isinstance(arg, Address):
                    buff = arg.get_variable().get_buffer()
                elif isinstance(arg, Variable):
                    buff = arg.get_buffer()
                if buff.alloctype == AllocType.HEAP:
                    statements_apicall += [SetNull(buff)]

        context.generate_auxiliary_operations()

        statements = []
        statements += context.generate_buffer_decl()
        statements += context.generate_buffer_init()
        statements += statements_apicall 

        clean_up_sec = context.generate_clean_up()
        counter_size = context.get_counter_size()
        stub_functions = context.get_stub_functions()

        d = Driver(statements, context)
        d.add_clean_up(clean_up_sec)
        d.add_counter_size(counter_size)
        d.add_stub_functions(stub_functions)

        return d