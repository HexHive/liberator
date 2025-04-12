from enum import Enum

class TypeTag(Enum):
    PRIMITIVE = 1
    STRUCT = 2
    FUNCTION = 3

class Type:
    token: str
    size: int
    # attributes!
    is_incomplete: bool
    is_const: bool
    tag: TypeTag
    
    def __init__(self, token, size = 0, is_incomplete = False, is_const = False, tag = TypeTag.PRIMITIVE):
        self.token          = token
        self.size           = size
        self.is_incomplete  = is_incomplete
        self.is_const       = is_const
        self.tag            = tag

    def __str__(self):
        sc = "1" if self.is_const else "0"
        return f"{self.__class__.__name__}(name={self.token},cons={sc})"
    
    def __repr__(self):
        return str(self)

    # for an element, the hash is just the key
    def __hash__(self):
        return hash(self.token + str(self.__class__.__name__))
        # return hash(self.token + str(self.__class__.__name__) + str(self.is_const))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def get_size(self):
        return self.size

    def get_token(self):
        return self.token
    
    def get_tag(self):
        return self.tag