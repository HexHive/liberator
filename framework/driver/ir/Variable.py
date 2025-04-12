from . import Value, Type, Address, Buffer

class Variable(Value):
    token: str
    index: int
    buffer: Buffer
    
    addr: Address.Address

    def __init__(self, token, index, buffer):
        self.token  = token
        self.index  = index
        self.buffer = buffer

        self.addr   = Address.Address(token, self)

    def get_index(self):
        return self.index

    def get_buffer(self):
        return self.buffer

    def get_token(self):
        return self.token

    def get_type(self):
        return self.buffer.get_type()

    def __str__(self):
        return f"{self.__class__.__name__}(name={self.token})"
    
    def __repr__(self):
        return str(self)

    # for an element, the hash is just the key + type
    def __hash__(self):
        return hash(self.token + str(self.__class__.__name__))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def get_address(self):
        return self.addr

    def get_allocated_size(self):
        # if the Variable is a pointer, I have to understand how many elements it is 
        # supposed to point to
        from . import PointerType
        if isinstance(self.get_type(), PointerType):
            raise NotImplementedError

        return self.get_type().get_size()