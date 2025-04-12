from . import Value, Type

class NullConstant(Value):
    type: Type

    def __init__(self, type):
        self.type = type

    # for an element, the hash is just the key + type
    def __hash__(self):
        return hash(hash(self.type) + hash(str(self.__class__.__name__)))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __str__(self):
        return f"{self.__class__.__name__}(name={self.type.token})"

    def __repr__(self):
        return str(self)