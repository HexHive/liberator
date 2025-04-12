from abc import ABC, abstractmethod

class DependencyGraphGenerator(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def create(self):
        pass