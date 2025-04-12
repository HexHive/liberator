from common import Api

class DependencyGraph:
    def __init__(self):
        self.graph = {}

    def add_edge(self, api_from: Api, api_to: Api):
        api_a_depdences = self.graph.get(api_from, set())
        api_a_depdences.add(api_to)
        self.graph[api_from] = api_a_depdences

    def keys(self):
        return self.graph.keys()

    def items(self):
        return self.graph.items()