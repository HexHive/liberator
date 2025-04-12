from . import Type

from common import DataLayout

class PointerType(Type):
    def __init__(self, token, type: Type, is_const: bool = False):
        super().__init__(token)
        self.type = type
        self.is_const = is_const
        # it makes sense because I always have poninter to functions
        self.to_function = False
        self.size = DataLayout.instance().infer_type_size("*")

    def get_pointee_type(self):
        return self.type

    def get_base_type(self):
        parent_type = self.get_pointee_type()

        if not isinstance(parent_type, PointerType):
            return parent_type

        return parent_type.get_base_type()
        
    def get_all_consts_str(self):
        return "".join(["1" if c else "0" for c in self.get_all_consts()])
    
    def get_all_consts(self):
        s = []
        tmp = self
        while isinstance(tmp, PointerType):
            s += [tmp.is_const]
            tmp = tmp.type
        s += [tmp.is_const]
        
        return s
    
    def __str__(self):
        sc = self.get_all_consts_str()
        return f"{self.__class__.__name__}(name={self.token},cons={sc})"