from abc import ABC, abstractmethod
from typing import List, Set, Dict, Tuple, Optional

from . import Statement, Type, Variable, Buffer

class ConstStringDecl(Statement):
    buffer:     Buffer
    string_val: str

    def __init__(self, buffer: Buffer, string_val: str):
        super().__init__()

        type = buffer.get_type()

        # I want a Pointer(Type), no multiple pointers, no base types
        if type.token != "char*" and type.token != "unsigned char*":
            # print("ConstStringDecl")
            # from IPython import embed; embed(); exit(1)
            raise Exception(f"ConstStringDecl accepts only 'char*', {type} received")

        self.buffer = buffer
        self.string_val = string_val

    # for an element, the hash is just the key + type
    def __hash__(self):
        return hash(self.token + str(self.__class__.__name__))

    def __str__(self):
        return f"{self.__class__.__name__}(name={self.buffer.get_token()})"

    def get_buffer(self):
        return self.buffer

    def get_string_val(self):
        return self.string_val