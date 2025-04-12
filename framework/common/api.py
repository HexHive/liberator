from typing import List
class Arg:
    name: str
    flag: str
    size: int
    type: str
    # these are attributes from my perspective
    is_const: List[bool]

    def __init__(self, name, flag, size, type, is_const):
        self.name = name
        self.flag = flag
        self.size = size
        self.type = type
        self.is_const = is_const

    def __str__(self):
        return f"Arg(name={self.name})"

    def __repr__(self):
        return str(self)

    def __key(self):
        arg_lst = []
        arg_lst += [self.name]
        arg_lst += [self.flag]
        arg_lst += [self.size]
        arg_lst += [self.type]
        arg_lst += ["".join([f"{x}" for x in self.is_const])]
        return tuple(arg_lst)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return hash(self) == hash(other) 

class Api:
    function_name: str
    is_vararg: bool
    return_info: Arg
    arguments_info: List[Arg]

    namespace: List[str]

    def __init__(self, function_name: str, is_vararg: bool, 
                    return_info: Arg, arguments_info: List[Arg],
                    namespace: List[str]):
        self.function_name = function_name
        self.is_vararg = is_vararg
        self.return_info = return_info
        self.arguments_info = arguments_info
        self.namespace = namespace

    def __str__(self):
        return f"Api(function_name={self.function_name})"

    def __repr__(self):
        return str(self)

    def __key(self):
        arg_lst = []
        arg_lst += [self.function_name]
        arg_lst += [self.is_vararg]
        arg_lst += [hash(self.return_info)]
        arg_lst += [hash(a) for a in self.arguments_info]
        arg_lst += [hash(a) for a in self.namespace]
        return tuple(arg_lst)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return hash(self) == hash(other) 