from typing import List, Set, Dict
import random, hashlib

from .ir import Type, PointerType, Variable, BuffDecl, BuffInit, Function
from .ir import Statement, Value, NullConstant, Buffer, AllocType, TypeTag
# from .ir import ConditionUnsat
from common import DataLayout

class Context:
    # trace the variable alives in this buffers within the context
    buffs_alive = Set[Buffer]
    # trace indexes to create new unique vars
    buffs_counter = Dict[Type, int]
    # trace stub functions for callback
    stub_functions = Dict[Type, Function]

    POINTER_STRATEGY_NULL = 0
    POINTER_STRATEGY_ARRAY = 1

    def __init__(self):
        self.buffs_alive = set()
        self.buffs_counter = {}
        self.stub_void = Type("void")
        self.stub_char_array = PointerType("char*", Type("char", 8))
        self.poninter_strategies = [Context.POINTER_STRATEGY_NULL, 
                                    Context.POINTER_STRATEGY_ARRAY]

        # special case a buffer of void variables
        self.buffer_void = Buffer("buff_void", 1, self.stub_void, 
            AllocType.STACK)
        self.buffs_alive.add(self.buffer_void)

        # TODO: make this from config?
        # self.MAX_ARRAY_SIZE = 1024
        self.MAX_ARRAY_SIZE = 512
        self.DOUBLE_PTR_SIZE = 16

        self.stub_functions = {}

        # TODO: map buffer and input
        # self.buffer_map = {}

    def is_void_pointer(self, arg):
        return isinstance(arg, PointerType) and arg.get_pointee_type() == self.stub_void

    def get_null_constant(self):
        return NullConstant(self.stub_void)

    def create_new_buffer(self, type, force_pointer: bool):
        # if "char" in type.token:
        #     print("create_new_buffer")
        #     from IPython import embed; embed(); exit(1)

        #     # "access": "create",
        #     # "fields": [],


        default_alloctype = AllocType.HEAP
            
        alloctype = AllocType.STACK
        if isinstance(type, PointerType):
            # if "UriQueryListW" in type.token:
            #     print("what allocatype I need?")
            #     from IPython import embed; embed(); exit(1)
            t_base = type.get_base_type()
            if (t_base.is_incomplete and 
                t_base.tag == TypeTag.STRUCT):
                alloctype = default_alloctype
            # if (DataLayout.instance().is_fuzz_friendly(t_base.get_token()) and
            #     t_base.tag == TypeTag.STRUCT):
            #     alloctype = default_alloctype
            if type.is_const:
                alloctype = default_alloctype
            if force_pointer:
                alloctype = default_alloctype

        # double pointers -> always in heap
        if DataLayout.is_ptr_level(type, 2):
            if type.get_base_type().is_incomplete:
                alloctype = default_alloctype
            else:
                alloctype = AllocType.HEAP
        #     # .get_token() in DataLayout.string_types
        # elif (isinstance(type, PointerType) and
            
            

        buff_counter = self.buffs_counter.get(type, 0)
        
        pnt = ""
        tt = type
        ps = ""
        while isinstance(tt, PointerType):
            ps += "p"
            tt = tt.get_pointee_type()
        if ps != "":
            pnt = f"_{ps}"
        cst = "c" if type.is_const else ""
        # so far, only HEAP and STACK
        decrt = ""
        if alloctype == AllocType.HEAP:
            decrt = "h" 
        elif alloctype == AllocType.STACK:
            decrt = "s"

        namespace_sep = "::"
        if namespace_sep in type.token:
            namespace_idx = type.token.index(namespace_sep) + len(namespace_sep)
            clean_token = type.token[namespace_idx:]
        else:
            clean_token = type.token
        buff_name = f"{clean_token}{pnt}_{cst}{decrt}{buff_counter}"
        buff_name = buff_name.replace(" ", "")
        # NOTE: char* => always considered as array!
        if ((type.token in DataLayout.string_types) and
            alloctype == AllocType.STACK):
            new_buffer = Buffer(buff_name, self.MAX_ARRAY_SIZE, type, alloctype)
        elif type.token == "char**":
            new_buffer = Buffer(buff_name, self.DOUBLE_PTR_SIZE, type, alloctype)
        else:
            new_buffer = Buffer(buff_name, 1, type, alloctype)

        self.buffs_alive.add(new_buffer)
        self.buffs_counter[type] = buff_counter + 1

        return new_buffer

    def create_new_var(self, type: Type, force_pointer: bool):

        # in case of void, I just return a void from a buffer void
        if type == self.stub_void:
            return self.buffer_void[0]

        buffer = self.create_new_buffer(type, force_pointer)

        # for the time being, I always return the first element
        return buffer[0]

    def get_allocated_size(self):
        return sum([ b.get_allocated_size() for b in self.buffs_alive ])

    def has_vars_type(self, type: Type) -> bool:
        for v in self.buffs_alive:
            if v.get_type() == type:
                return True

        return False

    def has_buffer_type(self, type: Type):
        for b in self.buffs_alive:
            if b.get_type() == type:
                return True

        return False

    def get_random_buffer(self, type: Type) -> Buffer:
        return random.choice([b for b in self.buffs_alive if b.get_type() == type])
    
    def get_random_var(self, type: Type) -> Variable:
        return self.get_random_buffer(type)[0]

    def randomly_gimme_a_var(self, type: Type, towhom, is_ret: bool = False) -> Value:

        v = None

        # if type.is_const and is_ret:
        #     print("type is const")
        #     from IPython import embed; embed(); exit(1)

        if isinstance(type, PointerType):
            is_incomplete = False
            if type.get_pointee_type().is_incomplete or is_ret:
                tt = type
                if not is_ret:
                    is_incomplete = type.get_pointee_type().is_incomplete
            else:
                tt = type.get_pointee_type()
                is_incomplete = tt.is_incomplete

            # If asking for ret value, I always need a pointer
            if (is_ret or
                type.get_base_type().token != "char"):
                a_choice = Context.POINTER_STRATEGY_ARRAY
            else:
                a_choice = random.choice(self.poninter_strategies)

            # just NULL
            if a_choice == Context.POINTER_STRATEGY_NULL:
                # print("choosing null")
                # from IPython import embed; embed(); exit(1)
                v = NullConstant(tt)
            # a vector
            elif a_choice == Context.POINTER_STRATEGY_ARRAY:
                # print("elif a_choice == Context.POINTER_STRATEGY_ARRAY:")
                pick_random = random.getrandbits(1) == 0

                if not self.has_vars_type(type):
                    # print("self.has_vars_type")
                    pick_random = False
                elif ((tt.tag == TypeTag.STRUCT and
                      not DataLayout.instance().is_fuzz_friendly(tt.token)) or 
                      is_incomplete):
                    # print("not DataLayout.instance().is_fuzz_friendly")
                    # if tt.token == "char":
                    #     from IPython import embed; embed(); exit(1)
                    pick_random = True                
                # elif not is_incomplete:
                #     pick_random = False
                elif is_ret:
                    pick_random = False

                vp = None
                if pick_random:
                    # print("self.get_random_buffer")
                    vp = self.get_random_buffer(type)
                else:
                    # print("self.create_new_buffer")
                    vp = self.create_new_buffer(type, is_ret)
                 
                # if vp is None:
                #     raise ConditionUnsat()

                # if ((random.getrandbits(1) == 0 or
                #     not self.has_vars_type(type, cond)) and 
                #     not is_incomplete):
                #     try:
                #         vp = self.create_new_buffer(type, cond, is_ret)
                #     except Exception as e:
                #         print("within 'a_choice == Context.POINTER_STRATEGY_ARRAY'")
                #         from IPython import embed; embed(); exit()
                # else:
                #     vp = self.get_random_buffer(type, cond)

                v = vp.get_address()

        else:
            # if "type" is incomplete, I can't get its value at all.
            # besides void!
            if type.is_incomplete and type != self.stub_void:
                raise Exception(f"Cannot get a value from {type}!")
 
            # if v not in context -> just create
            if not self.has_vars_type(type):
                # print(f"=> {t} not in context, new one")
                try:
                    v = self.create_new_var(type, is_ret)
                except:
                    print("within 'not self.has_vars_type(type):'")
                    from IPython import embed; embed(); exit()
            else:
                # I might get an existing one
                if random.getrandbits(1) == 1:
                    # print(f"=> wanna pick a random {t} from context")
                    v = self.get_random_var(type)
                # or create a new var
                else:
                    # print(f"=> decided to create a new {t}")
                    v = self.create_new_var(type, is_ret)

        if v is None:
            raise Exception("v was not assigned!")

        return v
    
    def generate_buffer_decl(self) -> List[Statement]:
        return [BuffDecl(x) for x in self.buffs_alive if x.get_type() != self.stub_void]

    def generate_buffer_init(self) -> List[Statement]:
        buff_init = []

        for x in self.buffs_alive:
            t = x.get_type()

            if isinstance(t, PointerType) and t.get_base_type().is_incomplete:
                continue

            if t.is_incomplete:
                continue
            
            if t == self.stub_void:
                continue
            
            buff_init += [BuffInit(x)]

        return buff_init

    def get_function_pointer(self, type: PointerType):
        
        if type in self.stub_functions:
            return self.stub_functions[type]
        
        # print("get_function_pointer")
        # from IPython import embed; embed(); exit(1)

        func_name = "f"+hashlib.md5(bytes(type.token, 'utf-8')).hexdigest()[:8]

        func = Function(func_name, type)
        self.stub_functions[type] = func

        return func
    
    def get_stub_functions(self):
        return self.stub_functions