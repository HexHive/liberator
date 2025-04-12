from typing import List, Set, Dict, Tuple, Optional
from abc import ABC, abstractmethod

# from . import Type

class BackendDriver(ABC):

    @abstractmethod
    def __init__(self, working_dir, seeds_dir, num_seeds):
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def emit_driver(self, driver, driver_filename):
        pass

    @abstractmethod
    def emit_seeds(self, driver, driver_filename):
        pass
    