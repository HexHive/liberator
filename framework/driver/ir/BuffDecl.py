from abc import ABC, abstractmethod
from typing import List, Set, Dict, Tuple, Optional

from . import Statement, Type, Variable, Buffer

class BuffDecl(Statement):
    buffer: Buffer

    def __init__(self, buffer):
        super().__init__()
        self.buffer = buffer
        # TODO: map buffer and input
        # self.buffer_map = {}

    # for an element, the hash is just the key + type
    def __hash__(self):
        return hash(self.token + str(self.__class__.__name__))

    def __str__(self):
        return f"{self.__class__.__name__}(name={self.buffer.get_token()})"

    def get_buffer(self):
        return self.buffer