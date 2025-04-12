from abc import ABC, abstractmethod

import copy, re

from common import Api, Utils, DataLayout

from driver import Driver
from driver.ir import Type, PointerType, ApiCall, TypeTag

class Factory(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def create_random_driver(self) -> Driver:
        pass

    @staticmethod
    def api_to_apicall(api: Api) -> ApiCall:
        function_name = api.function_name
        return_info = api.return_info
        arguments_info = api.arguments_info
        namespace = api.namespace

        # if function_name in ["pcap_next_ex"]:
        #     print(f"api_to_apicall: {function_name}")
        #     from IPython import embed; embed(); exit(1)

        arg_list_type = []
        for _, arg in enumerate(arguments_info):
            # NOTE: for simplicity, const type as arguments can be consider non-const, see `Driver_IR.md` for more info
            the_type = Factory.normalize_type(arg.type, arg.size, arg.flag, arg.is_const)
            arg_list_type += [the_type]

        if return_info.size == 0:
            ret_type = Factory.normalize_type('void', 0, "val", [False])
        else:
            ret_type = Factory.normalize_type(return_info.type, return_info.size, return_info.flag, return_info.is_const)
        
        return ApiCall(api, function_name, namespace, arg_list_type, ret_type)

    @staticmethod
    def normalize_type(a_type, a_size, a_flag, a_is_const) -> Type:
        
        if not isinstance(a_is_const, list):
            raise Exception(f"a_is_const must be a list, \"{type(a_is_const)}\" given!")
        
        if a_flag == "ref" or a_flag == "ret":
            if not re.search("\*$", a_type) and "*" in a_type:
                raise Exception(f"Type '{a_type}' is not a valid pointer")
        elif a_flag == "val":
            if "*" in a_type:
                raise Exception(f"Type '{a_type}' seems a pointer while expecting a 'val'")

        if a_flag == "fun" and "(*)" in a_type:

            a_type_core = a_type

            a_size_core = 0
            a_incomplete_core = True
            a_is_const = True
            type_tag = TypeTag.FUNCTION
            type_core = Type(a_type_core, a_size_core, a_incomplete_core, 
                             a_is_const, type_tag)
            
            return_type = PointerType(
                a_type_core + "*" , copy.deepcopy(type_core))

            return_type.to_function = True
        else:

            pointer_level = a_type.count("*")
            a_type_core = a_type.replace("*", "").replace(" ", "")
            
            # some types are fuck'd up. They need to be rebuilt.
            if a_type_core == "unsignedlonglong":
                a_type_core = "unsigned long long"
            if a_type_core == "longlong":
                a_type_core = "long long"
            if a_type_core == "unsignedlong":
                a_type_core = "unsigned long"
            if a_type_core == "unsignedint":
                a_type_core = "unsigned int"
            if a_type_core == "signedchar":
                a_type_core = "signed char"
            if a_type_core == "unsignedchar":
                a_type_core = "unsigned char"
            if a_type_core == "unsignedshort":
                a_type_core = "unsigned short"
            

            # if a_type == "void *":
            #     print(f"normalize_type {a_type_core}")
            #     from IPython import embed; embed()
            #     exit(1)

            # # THIS IS A DOUBLE CHECK, NOT SURE WE NEED IT, BETTER SAFE THAN SORRY!!
            # if a_type_core == "void":
            #     a_is_incomplete = True

            # NOTE: a_size comes wrong from LLVM analysis, I use this trick to fix
            # the size
            a_size = DataLayout.instance().get_type_size(a_type_core)
            a_incomplete_core = DataLayout.instance().is_incomplete(a_type_core)

            # is this guy a STRUCT or a PRIMITIVE?
            type_tag = TypeTag.PRIMITIVE
            if DataLayout.instance().is_a_struct(a_type_core):
                type_tag = TypeTag.STRUCT
                
            type_core = Type(a_type_core, a_size, a_incomplete_core, a_is_const[-1], type_tag)

            return_type = type_core
            for x in range(1, pointer_level + 1):
                return_type = copy.deepcopy(PointerType( a_type_core + "*"*x , copy.deepcopy(return_type), a_is_const[-(x+1)]))

            return_type.to_function = False
            
            if return_type.token == "unsignedlong":
                print("unsignedlong?")
                from IPython import embed; embed(); exit(1)

        return return_type
        
class EmptyDriverSpace(Exception):
    """EmptyDriverSpace, the factory can't generate any other driver"""
    def __init__(self):
        pass
