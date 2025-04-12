from abc import ABC, abstractmethod
from typing import List, Set, Dict, Tuple, Optional
from enum import Enum

from . import Statement, Type, Variable, PointerType

class AllocType(Enum):
    HEAP = 1
    STACK = 2
    GLOBAL = 3

class Buffer:
    # variables:  List[Variable]
    n_element:  int
    type:       Type
    alloctype:  AllocType

    def __init__(self, token, n_element, type, alloctype):
        self.token = token
        self.n_element = n_element
        self.type = type
        self.alloctype = alloctype

        self.variables = {}

    def __getitem__(self, key):
        if key < 0 or key >= self.n_element:
            raise KeyError

        self._init(key)

        return self.variables[key]

    def __setitem__(self, key, value):
        if key < 0 or key >= self.n_element:
            raise KeyError

        self.variables[key] = value

    def get_alloctype(self):
        return self.alloctype

    def get_type(self):
        return self.type

    def get_token(self):
        return self.token

    def get_number_elements(self):
        return self.n_element

    def _init(self, key):
        # lazy init, I set the variable if requested by somebody
        if key not in self.variables:
            self.variables[key] = Variable.Variable(f"{self.token}_{key}", key, self)

    def get_address(self):
        if self.n_element == 0:
            raise Exception(f"Can't get address from an empty buffer")

        self._init(0)
        return self.variables[0].get_address()

    def get_allocated_size(self):

        b_t = self.type
        if (isinstance(b_t, PointerType) and 
            self.alloctype == AllocType.STACK and 
            b_t.get_base_type().get_size() != 0):
            return self.n_element * b_t.get_base_type().get_size()
        else:
            if b_t.get_size() is None:
                print("Is none?")
                from IPython import embed; embed(); exit(1)
            return self.n_element * b_t.get_size()
