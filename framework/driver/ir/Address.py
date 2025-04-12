from typing import Union

from . import Value, Variable, Function

class Address(Value):
    token:      str
    variable:   Union["Variable", "Function"]

    def __init__(self, token, variable):
        self.token = token
        self.variable = variable

    def get_variable(self):
        return self.variable

    # for an element, the hash is just the key + type
    def __hash__(self):
        return hash(self.token + str(self.__class__.__name__))

    def __str__(self):
        return f"{self.__class__.__name__}(name={self.token})"
    
    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def get_token(self):
        return self.token