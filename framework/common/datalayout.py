from common import Utils

# Extract type system from library (only for structs):
#   - match llvm and clanv api file
#   - first, check if known from table
#   - second, check if in LLVM api
#   - third, check if in list of incomplete types
#   - fourth, get type from LLVM definition through LLVM name (add extraction from condition_extraction)
class DataLayout:
    # so far, only clang_str -> (size in bit)
    # layout:     Dict[str, int]
    # structs:    Set[str]
    # enum:       Set[str]

    _instance           : "DataLayout" = None
    
    size_types = ["size_t", "int", "uint32_t", "uint64_t", "__uint32_t", "unsigned int", "int64_t", "unsigned long", "__u_int", "__off_t"]

    string_types = ["char*", "unsigned char*", "wchar_t*", \
                    "u_char*", "u_char"]
    # string_types = ["char*", "unsigned char*", "wchar_t*", \
    #                 "char**", "unsigned char**", "wchar_t**" \
    #                 "u_char*", "u_char**"]

    def __init__(self):
        raise Exception("ConditionManager can be obtained through instance() class method")
    
    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    def setup(self, apis_clang_p: str, apis_llvm_p: str,
        incomplete_types_p: str, data_layout_p: str, enum_types_p: str):
        print("DataLayout populate!")

        self.layout = {}

        apis_clang = Utils.get_apis_clang_list(apis_clang_p)
        apis_llvm = Utils.get_apis_llvm_list(apis_llvm_p)
        incomplete_types = Utils.get_incomplete_types_list(incomplete_types_p)
        data_layout = Utils.get_data_layout(data_layout_p)
        enum_type = Utils.get_enum_types_list(enum_types_p)

        self.apis_clang = apis_clang
        self.apis_llvm = apis_llvm
        self.incomplete_types = incomplete_types
        self.data_layout = data_layout
        self.enum_type = enum_type
        self.clang_to_llvm_struct = {}

        # loop all the types in apis_clang (args + ret) and try to infer all the
        # types
        for function_name, api in apis_clang.items():

            if function_name not in self.apis_llvm:
                continue

            # if function_name == "GetX86CacheInfo":
            #     from IPython import embed; embed(); exit(1)
            for arg_pos, arg in enumerate(api["arguments_info"]):
                type_clang = arg["type_clang"]
                llvm_arg_flag = self.apis_llvm[function_name]["arguments_info"][arg_pos]["flag"]
                self.populate_table(type_clang, function_name, arg_pos, llvm_arg_flag)

            type_clang = api["return_info"]["type_clang"]
            llvm_arg_flag = self.apis_llvm[function_name]["return_info"]["flag"]
            self.populate_table(type_clang, function_name, -1, llvm_arg_flag)

        # print(self.layout)
        # from IPython import embed; embed(); exit(1)

    def get_llvm_type(self, function_name, arg_pos):
        if arg_pos == -1:
            arg = self.apis_llvm[function_name]["return_info"]
        else:
            arg = self.apis_llvm[function_name]["arguments_info"][arg_pos]

        l_type = arg["type"]
        l_size = arg["size"]

        return l_type, l_size

    
    def multi_level_size_infer(self, ttype: str, function_name: str, pos: int, is_original: bool):
        t_size = 0

        # if ttype == "cpu_features::CacheInfo" and pos == -1:
        #     print("multi_level_size_infer")
        #     from IPython import embed; embed(); exit(1)
        
        # sanity check for annoying spaces
        ttype = ttype.replace(" ", "")

        # first step, search in the tables
        known_type = False
        try:
            t_size = self.infer_type_size(ttype)
            known_type = True
        except:
            pass

        # if ttype == "TIFFCodec":
        #     print(f"{ttype}")
        #     from IPython import embed; embed(); exit(1)
        
        if not known_type:
            if function_name not in self.apis_llvm:
                raise Exception(f"{function_name} is not in self.apis_llvm")

            (type_llvm, size_llvm) = self.get_llvm_type(function_name, pos)

            if is_original and size_llvm != -1:
                t_size = size_llvm
            else:
                # type_llvm = type_llvm.replace("*", "")

                # if function_name == "cmsIsToneCurveMultisegment":
                # # if "cmsToneCurve" in type_llvm:
                #     from IPython import embed; embed(); exit(1)

                # I remove only the last *, if it exists
                # if type_llvm[-1] == "*":
                #     type_llvm = type_llvm[:-1]
                if "*" in type_llvm:
                    type_llvm = type_llvm.replace("*", "").replace(" ", "")
                if type_llvm in self.incomplete_types:
                    t_size = 0
                elif type_llvm in self.data_layout:
                    t_size = self.data_layout[type_llvm][0]
                    
                self.clang_to_llvm_struct[ttype] = type_llvm

        return t_size
    
    def populate_table(self, type_clang, function_name, arg_pos, arg_flag):

        # function ponters
        if arg_flag == "fun":
            t_size = self.multi_level_size_infer(type_clang, function_name, arg_pos, True)
            self.layout[type_clang.replace(" ", "")] = t_size
            return

        # remove pointers
        tmp_type = type_clang
        pointer_level = tmp_type.count("*")
        is_original = True
        while pointer_level > 0:

            t_size = self.multi_level_size_infer(tmp_type, function_name, arg_pos, is_original)
            self.layout[tmp_type.replace(" ", "")] = t_size

            tmp_type = tmp_type[:-1]
            pointer_level = tmp_type.count("*")
            is_original = False

        t_size = t_size = self.multi_level_size_infer(tmp_type, function_name, arg_pos, is_original)
        self.layout[tmp_type.replace(" ", "")] = t_size

        # if self.layout[type_clang] == 0:
        #     print(f"[DEBUG] size of {type_clang} is {self.layout[type_clang]}")
        #     print(f"[DEBUG] in fun {function_name}[{arg_pos}]")
        # from IPython import embed; embed(); exit(1)

    @staticmethod
    def is_ptr_level(type, lvl: int) -> bool:
        # from driver.ir.PointerType import PointerType

        # ptr_level = 0

        # tmp_type = type
        # while isinstance(tmp_type, PointerType):
        #     ptr_level += 1
        #     tmp_type = tmp_type.get_pointee_type()

        return DataLayout.get_ptr_level(type) == lvl
    
    @staticmethod
    def get_ptr_level(type) -> int:
        from driver.ir.PointerType import PointerType

        ptr_level = 0

        tmp_type = type
        while isinstance(tmp_type, PointerType):
            ptr_level += 1
            tmp_type = tmp_type.get_pointee_type()

        return ptr_level

    @staticmethod
    def is_a_pointer(type) -> bool:
        return "*" in type

    def infer_type_size(self, type) -> int:
        # given a clang-like type, try to infer its size
        # NOTE: table written for x86 64

        # any pointer is 8 byes in x86 64
        if DataLayout.is_a_pointer(type):
            return 8*8
        elif type == "float":
            return 4*8
        elif type == "double":
            return 8*8
        elif type == "int":
            return 4*8
        elif type == "unsigned int":
            return 4*8
        elif type == "long":
            return 8*8
        elif type == "unsigned long":
            return 8*8
        elif type == "char" or type == "signed char":
            return 1*8
        elif type == "void":
            return 0
        elif type == "size_t":
            return 8*8
        elif type == "uint8_t":
            return 8
        elif type == "uint32_t":
            return 4*8
        elif type == "uint64_t":
            return 8*8
        elif "(" in type:
            return 0
        elif type == "uint16_t":
            return 8*2
        elif type == "unsigned char":
            return 8
        elif type == "bool":
            return 8
        elif type == "wchar_t":
            return 8*4
        elif type == "unsigned short":
            return 8*2
        elif type == "unsigned long long":
            return 8*8
        elif type == "long long":
            return 8*8
        else:
            raise Exception(f"I don't know the size of '{type}'")

    def get_type_size(self, a_type: str) -> int:
        try:
            return self.infer_type_size(a_type)
        except:
            return self.layout[a_type]

    def is_a_struct(self, a_type: str) -> bool:

        if a_type not in self.clang_to_llvm_struct:
            return False
        
        if self.is_enum_type(a_type):
            return False
        
        a_llvm = self.clang_to_llvm_struct[a_type]

        if DataLayout.is_a_pointer(a_llvm):
            return False
        
        return True

        # return a_type in self.clang_to_llvm_struct

    def is_primitive_type(self, a_type: str) -> bool:
        return not self.is_a_struct(a_type)
        # try:
        #     self.infer_type_size(a_type)
        #     return True
        # except:
        #     return False
    
    def is_fuzz_friendly(self, a_type: str) -> bool:
        # for k, s in self.data_layout.items():
            # if 
        # if "TIFF" in a_type:
        #     print("is_a_struct")
        #     from IPython import embed; embed(); exit(1)

        # if not self.is_a_struct(a_type):
        #     return True

        if a_type not in self.clang_to_llvm_struct:
            return False
        
        # from IPython import embed; embed(); exit(1)
        llvm_type = self.clang_to_llvm_struct[a_type]

        # if llvm_type == "%struct.htp_hook_t":
        #     from IPython import embed; embed(); exit(1)

        if llvm_type not in self.data_layout:
            return False

        # 2nd position -> can feed from fuzzing seeds
        return self.data_layout[llvm_type][2]

    def has_incomplete_type(self) -> bool:
        return len(self.incomplete_types) != 0
    
    def is_enum_type(self, a_type: str) -> bool:
        return a_type in self.enum_type
    
    def has_user_define_init(self, a_type: str) -> bool:
        # NOTE: in somehow, I should define what types I can handle manually
        
        # if a_type == "UriParserStateA":
        #     return True
        
        # # if a_type == "UriUriA":
        # #     return True
        
        return False

    def is_incomplete(self, a_type: str) -> bool:
        
        tmp_type = "%" + a_type

        # # removing trailing stars
        # x = tmp_type
        # while x[-1] == "*":
        #     x = x[:-1]

        if "void" in tmp_type:
            # print("is void?")
            # from IPython import embed; embed(); exit(1)
            return True

        if tmp_type in self.incomplete_types:
            return True

        return False
