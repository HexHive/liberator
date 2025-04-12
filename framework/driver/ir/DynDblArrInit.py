from abc import ABC, abstractmethod
from typing import List, Set, Dict, Tuple, Optional

from . import Statement, Type, Variable, Buffer, PointerType
from common import DataLayout

class DynDblArrInit(Statement):
    buffer:     Buffer
    len_var:    Variable

    def __init__(self, buffer, len_var):
        super().__init__()

        buff_type = buffer.get_type()
        len_type = len_var.get_type()

        ptr_lvl = 0
        tmp_type = buff_type
        while isinstance(tmp_type, PointerType):
            ptr_lvl += 1
            tmp_type = tmp_type.get_pointee_type()

        base_type = buff_type.get_base_type()

        if ptr_lvl != 2:
            raise Exception(f" DynDblArrInit expects just a doubple ptr, \"{buff_type} is passed\"")

        # if base_type.get_token() not in ["char"]:
        #     raise Exception(f" DynDblArrInit expects \"char\" as buffer, \"{base_type}\" given instead")

        if len_type.get_token() not in DataLayout.size_types:
            raise Exception(f" DynDblArrInit expects \"size_t\" or \"int\" as len_Var, \"{len_type}\" given instead")

        self.buffer = buffer
        self.len_var = len_var

    # for an element, the hash is just the key + type
    def __hash__(self):
        return hash(self.token + str(self.__class__.__name__))

    def __str__(self):
        return f"{self.__class__.__name__}(name={self.buffer.get_token()})"

    def get_buffer(self):
        return self.buffer

    def get_len_var(self):
        return self.len_var