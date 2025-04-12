from abc import ABC, abstractmethod

class Statement(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def __hash__(self):
        pass

    @abstractmethod
    def __str__(self):
        pass
    
    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return hash(self) == hash(other)