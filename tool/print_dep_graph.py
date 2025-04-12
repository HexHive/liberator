#!/usr/bin/env python3

PROJECT_FOLDER="/workspaces/libfuzz"

import sys, os
sys.path.append(PROJECT_FOLDER)

import argparse
from framework import * 
from generator import Generator, Configuration
import logging, graphviz
import networkx as nx

logging.getLogger().setLevel(logging.WARN)
logging.getLogger("generator").setLevel(logging.DEBUG)


def __main():

    
    all_libs = ["c-ares", 
            "libaom", 
            "libpcap", 
            "libvpx", 
            "minijail", 
            "cpu_features", 
            "libhtp", 
            "libtiff", 
            "pthreadpool"]

    for lib in all_libs:
        if not lib == "libtiff":
            continue
        default_config = PROJECT_FOLDER + f"/targets/{lib}/generator.toml"
        # default_config = PROJECT_FOLDER + "/targets/c-ares/generator.toml"

        parser = argparse.ArgumentParser(description='Automatic Driver Generator')
        parser.add_argument('--config', type=str, help='The configuration', default=default_config)

        parser.add_argument('--overwrite', type=str, help='Set of parameters that overwrite the `config` toml file. Used to standardize configuration when testing multipe libraries.')

        parser.add_argument('--output', type=str, help='Where to save the .dot.', required=True)

        args = parser.parse_args()
        
        output = args.output
        config = Configuration(args.config, args.overwrite)

        dep_graph = config._config["generator"]["dep_graph"]
        dgraph = config.dependency_graph

        done_set = set()
        nodes = list(dgraph.keys())
        nodes_str = [n.function_name for n in nodes]
        inv_dep_graph = dict((k, set()) for k in nodes)
        for api, deps in dgraph.items():
            for dep in deps:
                if (dep,api) in done_set or (api,dep) in done_set:
                    continue

                if not dep in inv_dep_graph:
                    inv_dep_graph[dep] = set()

                inv_dep_graph[dep].add(api)
                done_set.add((dep,api))
    

        dot = graphviz.Graph(comment=f"DepGraph {dep_graph} for {default_config}")

        # dir_dep_graph = dict()
        # pair_don = set()
        # for n1 in nodes:
        #     for n2 in nodes:
        #         if (n1,n2) in pair_don or (n2,n1) in pair_don:
        #             continue
        #         if n1 in inv_dep_graph[n2] and n2 in inv_dep_graph[n1]:
        #             adj = dir_dep_graph.get(n1)
        #             adj.add(n2)
        #             dir_dep_graph[n1] = adj

        # transform in a direct graph
        for n, adj in inv_dep_graph.items():
            for nn in adj:
                dot.edge(n.function_name, nn.function_name)

        custom_api = PROJECT_FOLDER + f"/targets/{lib}/custom_apis_minized.txt"

        if not os.path.exists(custom_api):
            continue

        c_api = set()
        with open(custom_api, 'r') as f:
            for l in f:
                # from IPython import embed; embed(); exit(1)
                l = l.strip()
                if l not in nodes_str:
                    continue
                if not l:
                    continue
                c_api.add(l)

        G = nx.Graph()
        for n, adj in inv_dep_graph.items():
            for nn in adj:
                G.add_edge(n.function_name, nn.function_name)
            
        print(f"Library {lib}")
        print(G)


        print("APIs to work on:")
        print(c_api)
        # exit()
        print("clique intersection:")

        cliques = nx.find_cliques(G)
        l = sum([1 for x in cliques])
        
        print(f"#cliques {l}")

        already_done = set()
        for c in nx.find_cliques(G):
            i = c_api.intersection(set(c))
            if not i:
                continue
            if tuple(i) in already_done:
                continue
            print(i)
            already_done.add(tuple(i))
        
        print("="*30)

        # dot.save(output)
        # dot.render(directory='doctest-output', view=True)  

    # print("manual test")
    # from IPython import embed; embed(); exit(1)    

if __name__ == "__main__":
    __main()
