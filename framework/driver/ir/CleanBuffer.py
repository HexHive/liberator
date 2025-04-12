from abc import ABC, abstractmethod
from typing import List, Set, Dict, Tuple, Optional

from . import Statement, Type, Variable, Buffer, PointerType, AllocType


class CleanBuffer(Statement):
    buffer:     Buffer
    cleanup_method: str

    def __init__(self, buffer: Buffer, cleanup_method: str):
        super().__init__()

        type = buffer.get_type()

        # I want a Pointer(Type), no multiple pointers, no base types
        if not isinstance(type, PointerType):
            # and
            # buffer.get_alloctype() == AllocType.HEAP):
            # print("CleanBuffer")
            # from IPython import embed; embed(); exit(1)
            raise Exception(f"CleanBuffer accepts only PointerType to heap, {type} received")

        self.token = buffer.token
        self.buffer = buffer
        self.cleanup_method = cleanup_method

    # for an element, the hash is just the key + type
    def __hash__(self):
        return hash(self.token + str(self.__class__.__name__))

    def __str__(self):
        return f"{self.__class__.__name__}(name={self.buffer.get_token()})"

    def get_buffer(self):
        return self.buffer

    def get_cleanup_method(self):
        return self.cleanup_method