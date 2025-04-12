from typing import List, Set, Dict, Tuple, Optional

from common import Api
from . import Statement, Type, Value, PointerType, Address, Variable

class ApiCall(Statement):
    original_api:   Api
    function_name:  str
    namespace:      str
    arg_types:      List[Type]
    arg_vars:       List[Optional[Value]]
    max_vals:       List[int]
    ret_type:       Type
    ret_var:        Optional[Value]
    is_vararg:      bool
    vararg_var:     List[Optional[Value]]

    def __init__(self, api: Api, function_name: str, 
                 namespace: str, arg_types, ret_type):
        super().__init__()
        self.original_api   = api
        self.function_name  = function_name
        self.namespace      = namespace
        self.arg_types      = arg_types
        self.ret_type       = ret_type
        self.is_vararg      = api.is_vararg

        # these are the objects of the instance of the ApiCall
        self.arg_vars   = [None for x in arg_types]
        self.max_vals   = [0 for x in arg_types]
        self.ret_var    = None

        # NOTE: for the time being, one only argment for var arg
        if self.is_vararg:
            self.vararg_var = [None, None]

    def get_original_api(self) -> Api:
        return self.original_api

    def get_pos_args_types(self):
        return enumerate(self.arg_types)

    def set_pos_arg_var(self, pos: int, var: Value, max_val: int = 0):
        if pos < 0 or pos > len(self.arg_vars):
            raise Exception(f"{pos} out of range [0, {len(self.arg_vars)}]")

        # I must ensure the value is coherent with the argument type
        if isinstance(var, Variable) and isinstance(self.arg_types[pos], PointerType):
            raise Exception(f"{var} cannot be of type {self.arg_types[pos]}")

        if isinstance(var, Address) and not isinstance(self.arg_types[pos], Type):
            raise Exception(f"{var} cannot be of type {self.arg_types[pos]}")

        self.arg_vars[pos] = var

        if max_val != 0:
            self.max_vals[pos] = max_val
        
    def has_max_value(self, pos: int) -> bool:
        if pos < 0 or pos >= len(self.max_vals):
            return False
        
        return self.max_vals[pos] > 0

    def get_max_value(self, pos: int) -> int:
        if pos < 0 or pos >= len(self.max_vals):
            return -1
        
        return self.max_vals[pos]

    def set_ret_var(self, ret_var):

        if (isinstance(ret_var, Variable) and
            isinstance(self.ret_type, PointerType)):
            raise Exception(f"ret type is {self.ret_type} but giving {ret_var}")

        if (isinstance(ret_var, Address) and 
            not isinstance(self.ret_type, Type)):
            raise Exception(f"ret type is {self.ret_type} but giving {ret_var}")

        self.ret_var = ret_var

    # for an element, the hash is just the key + type
    def __hash__(self):
        return hash(self.function_name + str(self.__class__.__name__))

    def __str__(self):
        return f"{self.__class__.__name__}(name={self.function_name})"