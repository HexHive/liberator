import random

from . import Bias
from dependency import DependencyGraph
from common import Api 

class WBias(Bias):
    def __init__(self, dgraph: DependencyGraph):
        super().__init__()
        
        # DependencyGraph must be inverted, this is an "error". It probably
        # needs refactor in the future
        inv_dep_graph = dict((k, set()) for k in list(dgraph.keys()))
        for api, deps in dgraph.items():
            for dep in deps:
                if not dep in inv_dep_graph:
                    inv_dep_graph[dep] = set()
                
                inv_dep_graph[dep].add(api)
        self.dependency_graph = inv_dep_graph
        
        self.api_initial_weigth = {}
        self.api_frequency = {}
        for a in self.dependency_graph.keys():
            self.api_initial_weigth[a] = len(self.get_reachable_apis(a))
            self.api_frequency[a] = 0
            
    def get_reachable_apis(self, api):

        visited_api = set()
        working = [api]

        while(len(working) != 0):
            a = working.pop()
            for n in  self.dependency_graph[a]:
                if n in visited_api:
                    continue

                visited_api.add(n)
                working += [n]

        return visited_api
    
    def get_random_candidate(self, driver, candidate_api):
        w = []
        for ca in candidate_api:
            # Api object is in position 2
            w += [self.get_weigth(ca)]
        r_api = random.choices(candidate_api, weights=w)[0] 
        self.inc_api_frequency(r_api)
        return r_api
    
    def inc_api_frequency(self, api):
        freq = self.get_api_frequency(api)
        if freq is None:
            freq = 1
        else:
            freq = freq + 1
        self.set_api_frequency(api, freq)

    def get_weigth(self, api: Api):

        if api not in self.api_frequency:
            self.api_frequency[api] = 0
            self.api_initial_weigth[api] = max([w for _, w in self.api_initial_weigth.items()])

        if self.api_frequency[api] == 0:
            return self.api_initial_weigth[api]
        
        return float(self.api_initial_weigth[api])/self.api_frequency[api]
    
    def set_api_frequency(self, api, freq):
        if api not in self.api_frequency:
            return
        self.api_frequency[api] = freq

    def get_api_frequency(self, api):
        if api not in self.api_frequency:
            return None
        return self.api_frequency[api]
    
    ## PROBABLY THIS FUNCTION IS UNUSEFUL
    # def upd_api_frequency(self, api, rel_freq):
    #     if api not in self.api_frequency:
    #         return
    #     self.api_frequency[api] += rel_freq
    