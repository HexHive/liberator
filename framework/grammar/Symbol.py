from abc import ABC, abstractmethod

class Symbol(ABC):
    def __init__(self, name):
        self.name = name

    # for an element, the hash is just the key
    def __hash__(self):
        return hash(self.name + str(self.__class__.__name__))

    def __str__(self):
        return f"{self.__class__.__name__}(name={self.name})"
    
    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return hash(self) == hash(other)