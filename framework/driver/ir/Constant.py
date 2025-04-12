from typing import Any

from . import Value, Type

class Constant(Value):
    type: Type
    value: Any

    def __init__(self, type: Type, value: Any):
        self.type = type
        self.value = value

    # for an element, the hash is just the key + type
    def __hash__(self):
        return hash(hash(self.type) + hash(str(self.__class__.__name__)))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __str__(self):
        return f"{self.__class__.__name__}(name={self.type.token},value={self.value})"

    def __repr__(self):
        return str(self)
    
    def get_type(self):
        return self.type
    
    def get_value(self):
        return self.value