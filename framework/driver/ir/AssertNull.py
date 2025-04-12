from abc import ABC, abstractmethod
from typing import List, Set, Dict, Tuple, Optional

from . import Statement, Type, Variable, Buffer, PointerType


class AssertNull(Statement):
    buffer:     Buffer
    string_val: str

    def __init__(self, buffer: Buffer):
        super().__init__()

        type = buffer.get_type()

        # I want a Pointer(Type), no multiple pointers, no base types
        if not isinstance(type, PointerType):
            # print("AssertNull")
            # from IPython import embed; embed(); exit(1)
            raise Exception(f"AssertNull accepts only PointerType, {type} received")

        self.buffer = buffer

    # for an element, the hash is just the key + type
    def __hash__(self):
        return hash(self.token + str(self.__class__.__name__))

    def __str__(self):
        return f"{self.__class__.__name__}(name={self.buffer.get_token()})"

    def get_buffer(self):
        return self.buffer