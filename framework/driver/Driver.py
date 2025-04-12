from typing import List, Set, Dict, Tuple, Optional
from .ir import Statement, ApiCall, Function
from common import Api

class Driver:
    statements:     List[Statement]
    clean_up_sec:   List[Statement]
    counter_size:   List[int]
    stub_functions: List[Function]

    def __init__(self, statements, context):
        self.statements = statements
        self.context = context
        self.clean_up_sec = []
        self.counter_size = []
        self.stub_functions = []

    def __iter__(self):
        for s in self.statements:
            yield s
 
    def get_input_size(self):
        # the size if estimated at bits, we transform it into bytes
        return int(self.context.get_allocated_size()/8)
    
    def add_clean_up(self, clean_up_sec) -> 'Driver':
        self.clean_up_sec = clean_up_sec
        return self

    def add_counter_size(self, counter_size) -> 'Driver':
        self.counter_size = [int(c) for c in counter_size]
        return self

    def get_counter_size(self) -> List[int]:
        return self.counter_size
    
    def get_apis_multiset(self) -> Dict[Api, int]:

        api_multiset = {}
        for s in self.statements:
            if isinstance(s, ApiCall):
                api = s.original_api
                freq = api_multiset.get(api, 0) + 1
                api_multiset[api] = freq

        return api_multiset
    
    def add_stub_functions(self, stub_functions: List[Function]):
        self.stub_functions = stub_functions
        return self

    def get_stub_functions(self) -> List[Function]:
        return self.stub_functions