from typing import List, Set, Dict, Tuple, Optional, Any

import random, string, traceback, sys

from driver import Context
from driver.ir import Variable, Type, Value, PointerType, AllocType, CleanBuffer, CleanDblBuffer
from driver.ir import Address, NullConstant, Buffer, ConstStringDecl, ApiCall
from driver.ir import BuffDecl, BuffInit, FileInit, Statement, DynArrayInit
from driver.ir import SetStringNull, TypeTag, Function, DynDblArrInit, Constant
from . import Conditions, ConditionManager
from common.conditions import *
from common import DataLayout

class RunningContext(Context):
    variables_alive     : List[Variable]
    var_to_cond         : Dict[Variable, Conditions]
    file_path_buffers   : Set[Buffer]
    new_vars            : Set[Tuple[Variable, Variable, Conditions]]
    const_strings       : Dict[Variable, str]

    # static dictionary
    type_to_hash        : Dict[str, str]
    
    def __init__(self):
        super().__init__()
        self.variables_alive = []
        self.var_to_cond = {}

        self.file_path_buffers = set()
        self.new_vars = set()
        self.const_strings = {}

        self.poninter_strategies = [Context.POINTER_STRATEGY_ARRAY]

        self.auxiliary_operations_set = False
        self.buff_init = None
        self.counter_size = None

        self.DOUBLE_PTR_SIZE = 16

    # override of Context method
    def has_vars_type(self, type: Type, cond: ValueMetadata) -> bool:

        # FLAVIO: I think this should be like that!
        # TODO: Extract "base" type with a dedicated method?
        # tt = None
        # if isinstance(type, PointerType):
        #     if type.get_pointee_type().is_incomplete:
        #         tt = type
        #     else:
        #         tt = type.get_pointee_type()
        # else:
        #     tt = type
            
        # if tt is None:
        #     raise Exception("can't find a type for 'tt'")
        # tt = type

        for v in self.variables_alive:
            if self.var_is_equal_to_type_cond(v, type, cond):
                return True
            # if (v.get_type() == type and 
            #     self.var_to_cond[v].is_compatible_with(cond)):
            #     return True
            # if ((v.get_type() == tt or v.get_type() == type) and 
            #     self.var_to_cond[v].is_compatible_with(cond)):
            #     return True

        # if cond.is_array:
        #     from IPython import embed; embed(); exit(1)

        return False

    # def get_value_that_satisfy(self, type: Type,
    #         cond: AccessTypeSet) -> Optional[Value]:

    #     # print("Debug get_value_that_satisfy")
    #     # from IPython import embed; embed(); exit()

    #     tt = None
    #     if isinstance(type, PointerType):
    #         if type.get_pointee_type().is_incomplete:
    #             tt = type
    #         else:
    #             tt = type.get_pointee_type()
    #     else:
    #         tt = type
            
    #     if tt is None:
    #         raise Exception("can't find a type for 'tt'")

    #     vars = set()

    #     for v in self.variables_alive:
    #         if ((v.get_type() == tt or v.get_type() == type) and
    #             self.var_to_cond[v].is_compatible_with(cond)):
    #             vars.add(v)

    #     if len(vars) == 0:
    #         return None
    #     else:
    #         var = random.choice(list(vars))
    #         if isinstance(type, PointerType):
    #             return var.get_address()
    #         return var

    def get_value_that_strictly_satisfy(self, type: Type,
            cond: AccessTypeSet) -> Optional[Value]:

        # print("Debug get_value_that_strictly_satisfy")
        
        dl = DataLayout.instance()

        # if type.token == 'hostent*':
        #     print("get_value_that_strictly_satisfy")
        #     from IPython import embed; embed(); exit()    

        vars = set()
        
        if isinstance(type, PointerType) and dl.is_a_struct(type.get_pointee_type().token):
            for v in self.variables_alive:
                if (isinstance(v.get_type(), PointerType) and 
                    DataLayout.is_ptr_level(v.get_type(), 2) and 
                    v.get_type().get_pointee_type() == type and 
                    self.var_to_cond[v].is_compatible_with(cond)):
                    vars.add(v)
            
        for v in self.variables_alive:
            if (v.get_type() == type and 
                self.var_to_cond[v].is_compatible_with(cond)):
                vars.add(v)

        if len(vars) == 0:
            return None
        else:
            var = random.choice(list(vars))
            if isinstance(type, PointerType):
                return var.get_address()
            return var


    def add_variable(self, val: Value, cond: ValueMetadata):

        if not isinstance(val, Variable):
            raise Exception(f"{val} is not a Variable! :(")

        seek_val = None
        for v in self.variables_alive:
            if v == val:
                seek_val = v
                break

        if seek_val is None:
            self.variables_alive += [val]
            if cond != None:
                self.var_to_cond[val] = Conditions(cond)
        else:
            if cond != None:
                self.var_to_cond[val].add_conditions(cond.ats)
                self.var_to_cond[val].is_array = cond.is_array
                self.var_to_cond[val].is_malloc_size = cond.is_malloc_size
                self.var_to_cond[val].is_file_path = cond.is_file_path
                # self.var_to_cond[val].len_depends_on = cond.len_depends_on

        # TODO: handle dependency fields here?

    attempt = 2

    # def try_to_get_var(self, type: Type, cond: ValueMetadata, api_name: Api,
    #                     arg_pos: int) -> Value:
    def try_to_get_var(self, api_call: ApiCall, api_cond: FunctionConditions,
                       arg_pos: int) -> Value:

        # my convention: arg_pos -1 => return value
        is_ret = arg_pos == -1

        if is_ret:
            cond = api_cond.return_at
            type = api_call.ret_type
        else:
            cond = api_cond.argument_at[arg_pos]
            type = api_call.arg_types[arg_pos]
   
        # if (isinstance(type, PointerType) and 
        # type.get_base_type().token == "TIFF" and 
        # if arg_pos == -1 and api_call.function_name == "pcap_geterr":
        # if (isinstance(type, PointerType) and 
        #     type.get_base_type().token == "char" and api_call.function_name == "foo"):
        #     RunningContext.attempt -= 1

        # if (arg_pos == 0 and api_call.function_name == "ares_free_hostent"):
        #     print(f"try_to_get_var {type}")
        #     from IPython import embed; embed(); exit(1)

        is_sink = ConditionManager.instance().is_sink(api_call)
        is_source = ConditionManager.instance().is_source(cond)
        is_init = ConditionManager.instance().is_init(api_call, arg_pos)
        is_setby = ConditionManager.instance().is_setby(api_call, arg_pos)
        
        # if api_call.function_name == "TIFFCIELabToRGBInit" and arg_pos == 0:
        #     is_setby = True
        #     print(f"try_to_get_var {type}")
        #     from IPython import embed; embed(); exit(1)
        
        # if (api_call.function_name == "TIFFCIELabToXYZ" and 
        #     arg_pos == 0):
        #     # self.attempt -= 1
        #     print(f"try_to_get_var {type}")
        #     from IPython import embed; embed(); exit(1)

        val = None
        
        
        # if arg_pos == 0 and type.token == "htp_tx_t*":
        #     print(f"try_to_get_var {type}")
        #     is_setby = True
        #     # from IPython import embed; embed(); exit(1)

        # for variables used in ret -> I take any compatible type and overwrite
        # their conditions
        if is_ret:

            # if I need a void for return, don't bother too much
            if type == self.stub_void:
                val = NullConstant(self.stub_void)
            elif is_source:
                val = self.create_new_var(type, cond, is_ret)
                if (isinstance(val, Variable) and 
                    isinstance(val.get_type(), PointerType)):
                    val = val.get_address()
            else:
                val = self.randomly_gimme_a_var(type, cond, is_ret)

        elif is_sink:
            val = self.get_value_that_strictly_satisfy(type, cond)
            if val is None:
                if (Conditions.is_unconstraint(cond) and 
                    not type.is_incomplete):
                    val = self.randomly_gimme_a_var(type, cond, is_ret)
                else:
                    # raise ConditionUnsat()
                    raise ConditionUnsat(traceback.format_stack())
        # FLAVIO: this is an attempt to introduce NULL values in the code. It
        # does not working as expected so left it here for future refactor elif
        #     (random.randrange(1, 6) == 1 and isinstance(type, PointerType)):
        # val = NullConstant(self.stub_void) special case for void* types
        elif (isinstance(type, PointerType) and 
            type.get_pointee_type() == self.stub_void and 
            not ConditionManager.instance().custom_voidp_source):
            new_buff = self.create_new_var(self.stub_char_array, cond, False)
            val = new_buff.get_address()
        elif is_init or is_setby:
            # tt = None
            # if isinstance(type, PointerType):
            #     if type.get_pointee_type().is_incomplete:
            #         tt = type
            #     else:
            #         tt = type.get_pointee_type()
            # else:
            #     tt = type

            for v in self.variables_alive:
                # skip variables with different types and with incompatible
                # conds
                # if (not ((v.get_type() == tt or v.get_type() == type) and 
                #     self.var_to_cond[v].is_compatible_with(cond))):
                #     continue
                if not self.var_is_equal_to_type_cond(v, type, cond):
                    continue

                c = self.var_to_cond[v]
                if not c.is_init():
                    val = v
                    break
                    
            if val is None:
                val = self.create_new_var(type, cond, is_ret)

            if (isinstance(val, Variable) and 
                isinstance(type, PointerType)):
                val = val.get_address()
        elif self.has_vars_type(type, cond):
            try:
                # val = self.randomly_gimme_a_var(type, cond, is_ret)
                val = self.get_random_var(type, cond)
                if (isinstance(val, Variable) and 
                    isinstance(val.get_type(), PointerType)):
                    val = val.get_address()
            except Exception as e:
                print("randomly_gimme_a_var empty?!")
                from IPython import embed; embed(); exit(1)
                # else:
                #     raise ConditionUnsat()
        else:
            raise_an_exception = False

            # print("else:")
            if isinstance(type, PointerType):
                tt = type.get_base_type()  
            else:
                tt = type

            # check if the ats allows us to generate an object
            if not is_ret:
                if not DataLayout.is_ptr_level(type, 2):
                    if tt.is_incomplete:
                        # raise ConditionUnsat()
                        raise_an_exception = True
                    if tt.tag == TypeTag.STRUCT:
                        call_can_be_done = self.is_init_api(api_call, api_cond, arg_pos)
                        type_is_friendly = DataLayout.instance().is_fuzz_friendly(tt.token)
                        needs_init_or_setby = ConditionManager.instance().needs_init_or_setby(type)
                        
                        # if (api_call.function_name == "TIFFCIELabToXYZ" and 
                        #     arg_pos == 0):
                        #     # self.attempt -= 1
                        #     print(f"try_to_get_var {type} and {arg_pos}")
                        #     from IPython import embed; embed(); exit(1)
                        
                        if (not call_can_be_done and 
                            type_is_friendly and needs_init_or_setby):                            
                            raise_an_exception = True
                    if ConditionManager.instance().has_source(tt):
                        raise_an_exception = True
                # print(f"{tt}is not fuzz friendly")
                # from IPython import embed; embed(); exit(1)
                # raise ConditionUnsat()
                
            elif ((not Conditions.is_unconstraint(cond) or
                tt.is_incomplete) and 
                not DataLayout.instance().has_user_define_init(tt.token)):
                # print(f"no has_user_define_init for {tt}")
                # from IPython import embed; embed(); exit(1)
                # raise ConditionUnsat()
                raise_an_exception = True
            
            if raise_an_exception:
                raise ConditionUnsat(traceback.format_stack())
            else:
                val = self.create_new_var(type, cond, is_ret)
                if (isinstance(val, Variable) and 
                    isinstance(val.get_type(), PointerType)):
                    val = val.get_address()

        if val == None:
            raise Exception("Val unset")

        var_t = None
        if isinstance(val, Address):
            var_t = val.get_variable()
        elif isinstance(val, Variable):
            var_t = val
        is_heap_wo_len = (not isinstance(val, NullConstant) and
            cond.len_depends_on == "" and
            var_t.get_buffer().get_alloctype() == AllocType.HEAP and 
            var_t.get_type().get_base_type().get_tag() == TypeTag.PRIMITIVE and 
            var_t.get_type().get_base_type() != self.stub_void)
        
        # is_heap_wo_len_OLD = (not isinstance(val, NullConstant) and
        #     cond.len_depends_on == "" and
        #     var_t.get_buffer().get_alloctype() == AllocType.HEAP and 
        #     var_t.get_type().get_base_type().get_tag() == TypeTag.PRIMITIVE)
        
        # if is_heap_wo_len_OLD != is_heap_wo_len:
        #     print("INFO: I saved you ass!", file=sys.stderr)

        is_file_path = (cond.is_file_path and 
            not isinstance(val, NullConstant))

        if is_file_path:
            # print("cond.is_file_path")
            # from IPython import embed; embed(); exit(1)

            var = None
            if isinstance(val, Address):
                var = val.get_variable()
            elif isinstance(val, Variable):
                var = val
            else:
                raise Exception("Excepted Address or Variable")
            
            x_type = var.get_type()
            if isinstance(var, PointerType):
                x_type = var.get_base_type()
            
            if x_type.token in DataLayout.string_types:
            
                # buff = var.get_buffer()
                # buff.alloctype = AllocType.GLOBAL
                
                buff = var.get_buffer()
                (len_dep, len_cond) = self.create_dependency_length_variable()

                # if buff.get_type().token != "char*":
                #     print("checking type")
                #     from IPython import embed; embed(); exit(1)

                self.file_path_buffers.add(buff)
                self.new_vars.add((var, len_dep, len_cond))

                length = 20
                letters = string.ascii_lowercase
                file_name = ''.join(random.choice(letters) for i in range(length)) + ".bin"

                # print("is_File_path")
                # from IPython import embed; embed(); exit(1)
                # TODO: add folder to the file lenght
                self.const_strings[var] = file_name
        elif is_heap_wo_len:
            var = None
            if isinstance(val, Address):
                var = val.get_variable()
            elif isinstance(val, Variable):
                var = val
            else:
                raise Exception("Excepted Address or Variable")
            
            # print("is_heap_wo_len")
            # from IPython import embed; embed(); exit(1)
            
            (len_dep, len_cond) = self.create_dependency_length_variable()
            self.new_vars.add((var, len_dep, len_cond))

        return val
    
    # def should_have_init_or_setby(self, api_call: ApiCall, api_cond: FunctionConditions, 
    #                 arg_pos: int) -> bool:
    
    #     if arg_pos == -1:
    #         return False
        
    #     cm = ConditionManager.instance()
        
    #     cm.is_init(api_call, arg_pos)

    #     if len(cond.setby_dependencies) == 0:
    #         return False

    #     arg_ok = 0
    #     for d in cond.setby_dependencies:
    #         p_idx = int(d.replace("param_", ""))
    #         d_type = api_call.arg_types[p_idx]
    #         d_cond = api_cond.argument_at[p_idx]

    #         if self.has_vars_type(d_type, d_cond):
    #             arg_ok += 1
    #         elif d_type.tag == TypeTag.STRUCT:
    #             tt = d_type
    #             if isinstance(d_type, PointerType):
    #                 tt = d_type.get_base_type()
    #             if (DataLayout.instance().is_fuzz_friendly(tt.get_token()) or
    #                 not tt.is_incomplete):
    #                 arg_ok += 1
    #         elif d_type.tag == TypeTag.PRIMITIVE:
    #             arg_ok += 1

    #     # the idea is that I can control all the dependncies
    #     return arg_ok == len(cond.setby_dependencies)
    
    def is_init_api(self, api_call: ApiCall, api_cond: FunctionConditions, 
                    arg_pos: int) -> bool:
        
        # api_name = api_call.function_name
        # if api_name == "aom_codec_decode" and arg_pos == 0:
        #     print("is_init_api")
        #     from IPython import embed; embed(); exit(1)

        if arg_pos == -1:
            cond = api_cond.return_at
        else:
            cond = api_cond.argument_at[arg_pos] 

        if len(cond.setby_dependencies) == 0:
            return False

        arg_ok = 0
        for d in cond.setby_dependencies:
            p_idx = int(d.replace("param_", ""))
            d_type = api_call.arg_types[p_idx]
            d_cond = api_cond.argument_at[p_idx]

            if self.has_vars_type(d_type, d_cond):
                arg_ok += 1
            elif d_type.tag == TypeTag.STRUCT:
                tt = d_type
                if isinstance(d_type, PointerType):
                    tt = d_type.get_base_type()
                is_setby = ConditionManager.instance().is_setby(api_call, arg_pos)
                is_init = ConditionManager.instance().is_setby(api_call, arg_pos)
                if ((DataLayout.instance().is_fuzz_friendly(tt.get_token()) and 
                     not is_setby and not is_init) or
                    not tt.is_incomplete):
                    arg_ok += 1
            elif d_type.tag == TypeTag.PRIMITIVE:
                arg_ok += 1

        # the idea is that I can control all the dependncies
        return arg_ok == len(cond.setby_dependencies)

    def create_dependency_length_variable(self):
        len_type = Type("size_t", DataLayout.instance().get_type_size("size_t"))
        ats = AccessTypeSet()
        mdata = ValueMetadata(ats, False, False, False, "", [])
        return (self.create_new_var(len_type, mdata, False), mdata)

    def create_new_buffer(self, type: Type, cond: ValueMetadata, force_pointer: bool):
        
        # if "char" in type.token:
        #     print("create_new_buffer")
        #     from IPython import embed; embed(); exit(1)

        #     # "access": "create",
        #     # "fields": [],


        default_alloctype = AllocType.HEAP
        if not ConditionManager.instance().is_source(cond):
            default_alloctype = AllocType.GLOBAL
            
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
            if cond.len_depends_on != "":
                alloctype = AllocType.HEAP
            # if type.is_const:
            #     alloctype = default_alloctype
            if force_pointer:
                alloctype = default_alloctype
                
        # if isinstance(type, PointerType) and type.get_token() == "int*" and not force_pointer:
        #     print("int*??")
        #     from IPython import embed; embed(); exit(1)

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
        elif alloctype == AllocType.GLOBAL:
            decrt = "g"

        namespace_sep = "::"
        if namespace_sep in type.token:
            namespace_idx = type.token.index(namespace_sep) + len(namespace_sep)
            clean_token = type.token[namespace_idx:]
        else:
            clean_token = type.token
        buff_name = f"{clean_token}{pnt}_{cst}{decrt}{buff_counter}"
        buff_name = buff_name.replace(" ", "")
        # NOTE: char* => always considered as array!
        if ((cond.is_array or type.token in DataLayout.string_types) and
            alloctype == AllocType.STACK):
            new_buffer = Buffer(buff_name, self.MAX_ARRAY_SIZE, type, alloctype)
        elif type.token == "char**" or type.token == "char const**":
            new_buffer = Buffer(buff_name, self.DOUBLE_PTR_SIZE, type, alloctype)
        else:
            new_buffer = Buffer(buff_name, 1, type, alloctype)

        self.buffs_alive.add(new_buffer)
        self.buffs_counter[type] = buff_counter + 1

        return new_buffer
    
    def create_new_const_int(self, value: Any):
        type_token = "int"
        type_size = DataLayout.instance().get_type_size(type_token)
        type = Type(type_token, type_size)
        return Constant(type, value)

    def create_new_var(self, type: Type, cond: ValueMetadata, force_pointer: bool):

        # in case of void, I just return a void from a buffer void
        if type == self.stub_void:
            return self.buffer_void[0]

        buffer = self.create_new_buffer(type, cond, force_pointer)

        # for the time being, I always return the first element
        return buffer[0]

    def has_dereference(self, cond: ValueMetadata):

        has_deref = False
        for at in cond.ats:
            if at.fields == [-1]:
                has_deref = True
                break

        return has_deref

    def randomly_gimme_a_var(self, type: Type, cond: ValueMetadata,
        is_ret: bool = False) -> Value:

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
            if (is_ret or cond.is_file_path or 
                self.has_dereference(cond) or
                cond.len_depends_on != "" or
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

                if not self.has_vars_type(type, cond):
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
                    vp = self.get_random_buffer(type, cond)
                else:
                    # print("self.create_new_buffer")
                    vp = self.create_new_buffer(type, cond, is_ret)
                 
                if vp is None:
                    raise ConditionUnsat()

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
            if not self.has_vars_type(type, cond):
                # print(f"=> {t} not in context, new one")
                try:
                    v = self.create_new_var(type, cond, is_ret)
                except:
                    print("within 'not self.has_vars_type(type):'")
                    from IPython import embed; embed(); exit()
            else:
                # I might get an existing one
                if random.getrandbits(1) == 1:
                    # print(f"=> wanna pick a random {t} from context")
                    v = self.get_random_var(type, cond)
                # or create a new var
                else:
                    # print(f"=> decided to create a new {t}")
                    v = self.create_new_var(type, cond, is_ret)

        if v is None:
            raise Exception("v was not assigned!")

        return v

    def get_random_buffer(self, type: Type, cond: ValueMetadata) -> Buffer:
        return self.get_random_var(type, cond).buffer
    
    def var_is_equal_to_type_cond(self, var: Variable, type: Type,
                                  cond: ValueMetadata) -> bool:
        # if ((v.get_type() == tt or v.get_type() == type)
        #     and self.var_to_cond[v].is_compatible_with(cond)):
        
        # if type.token == "char*":
        #     print("var_is_equal_to_type_cond")
        #     from IPython import embed; embed(); exit(1)
        
        if self.var_to_cond[var].len_depends_on is not None:
            return False
            
        if (isinstance(var.get_type(), PointerType) and 
            any(var.get_type().get_all_consts())):
            return False
        
        if (isinstance(var.get_type(), PointerType) and 
            DataLayout.get_ptr_level(var.get_type()) == 2 and
            var.get_type().get_pointee_type() == type and
            self.var_to_cond[var].is_compatible_with(cond)):
            return True    
        
        if (var.get_type() == type and
            self.var_to_cond[var].is_compatible_with(cond)):
            return True
        
        return False
    
    def get_random_var(self, type: Type, cond: ValueMetadata) -> Variable:

        suitable_vars = []

        # tt = None
        # if isinstance(type, PointerType):
        #     if type.get_pointee_type().is_incomplete:
        #         tt = type
        #     else:
        #         tt = type.get_pointee_type()
        # else:
        #     tt = type

        for v in self.variables_alive:
            if self.var_is_equal_to_type_cond(v, type, cond):
                suitable_vars += [v]
            # if ((v.get_type() == tt or v.get_type() == type)
            #     and self.var_to_cond[v].is_compatible_with(cond)):
            #     suitable_vars += [v]

        return random.choice(suitable_vars)

        # return self.get_random_buffer(type, cond)[0]

    def infer_type(self, type, cond, fields):
        type_str = ""
        type_hash = ""

        if fields == []:
            type_strings = set()
            for x in cond.ats.access_type_set:
                if x.fields == []:
                    type_strings.add(x.type_string)

            if len(type_strings) == 0:
                type_str = type.token
                length = 20
                letters = string.ascii_lowercase
                type_hash = ''.join(random.choice(letters) for i in range(length))
            else:
                type_hash = None
                for t in type_strings:
                    if t in RunningContext.type_to_hash:
                        type_str = t
                        type_hash = RunningContext.type_to_hash[t]
                        break

            if not type_hash:
                raise Exception(f"Cannot find type hash for {type_strings}")
            
        elif fields == [-1]:
            
            type_strings = set()
            for x in cond.ats.access_type_set:
                if x.fields == []:
                    type_strings.add(x.type_string)

            if len(type_strings) == 0:
                # from IPython import embed; embed(); exit(1)
                # raise Exception("Not found type at [-1]")
                # print("Not found type at [-1]")
                type_strings.add(type.get_token())
            
            type_strs = []
            type_hash = None
            for t in type_strings:
                # I care only of 1-d pointers 
                if "*" not in t:
                    continue
                if t in RunningContext.type_to_hash:
                    type_strs += [t[:-1]]
            
            if len(type_str):
                raise Exception(f"Cannot find type hash for {type_strings}")

            type_hash = None
            type_str = None
            for s in type_strs:
                if s in RunningContext.type_to_hash:
                    type_hash = RunningContext.type_to_hash[s]
                    type_str = s
                    break

            # if I can't find anchestor, just produce a random hash
            if type_hash is None:
                length = 20
                letters = string.ascii_lowercase
                type_hash = ''.join(random.choice(letters) for i in range(length))
            
            if type_str is None:
                if isinstance(type, PointerType):
                    tkn = type.get_token()
                    type_str = tkn.replace("*", "", 1)
                elif len(type_strs) == 1:
                    type_str = type_strs[0]
                else:
                    print(f"Really don't know what to do with {type_strings}")
                    from IPython import embed; embed(); exit(1)
                    raise Exception(f"Really don't know what to do with {type_strings}")
                

        else:
            raise Exception(f"Cannot handle {fields} field type inferring")

        RunningContext.type_to_hash[type_str] = type_hash

        return (type_str, type_hash)
    
    def update_var(self, val: Optional[Value], cond: ValueMetadata,
                   is_ret: bool = False, is_sink: bool = False,
                   is_init: bool = False, is_set: bool = False):
        synthetic_cond = None

        var = None
        if isinstance(val, Variable):
            type = val.get_type()
            (type_str, type_hash) = self.infer_type(type, cond, [])
            x = AccessType(Access.WRITE, [], type_hash, type_str)
            synthetic_cond = AccessTypeSet(set([x]))
            var = val
        elif isinstance(val, Address):
            type = val.get_variable().get_type()
            (type_str, type_hash) = self.infer_type(type, cond, [])
            x0 = AccessType(Access.WRITE, [], type_hash, type_str)
            (type_str, type_hash) = self.infer_type(type, cond, [-1])
            x1 = AccessType(Access.WRITE, [-1], type_hash, type_str)
            x1.parent = x0
            synthetic_cond = AccessTypeSet(set([x0, x1]))
            var = val.get_variable()
        # Constant Values do not need to update conditions
        elif isinstance(val, Constant):
            return
        else:
            raise Exception(f"I don't know this val: {val}")

        if is_ret and var in self.variables_alive:
            del self.var_to_cond[var]
            self.variables_alive.remove(var)
            self.remove_from_new_vars(var)

        already_present = var in self.var_to_cond
        self.add_variable(var, cond)

        if already_present and is_sink:
            del self.var_to_cond[var]
            self.variables_alive.remove(var)
            # double check
            self.remove_from_new_vars(var)

        if var in self.var_to_cond and synthetic_cond is not None:
            self.var_to_cond[var].add_conditions(synthetic_cond)

            if is_init or is_set:
                self.var_to_cond[var].set_init()
            if is_sink:
                self.var_to_cond[var].unset_init()

            # from IPython import embed; embed(); exit(1);
            # import pdb; pdb.set_trace(); exit(1);

    def remove_from_new_vars(self, var: Variable):
        to_remove = None
        for var_h, len, cond in self.new_vars:
            if var_h == var:
                to_remove = (var_h, len, cond)

        if to_remove is not None:
            self.new_vars.remove(to_remove)

    def update(self, api_call: ApiCall, cond: ValueMetadata, 
               arg_pos: int):

        # my convention: arg_pos -1 => return value
        is_ret = arg_pos == -1

        if is_ret:
            # type = api_call.ret_type
            val = api_call.ret_var
        else:
            # type = api_call.arg_types[arg_pos]
            val = api_call.arg_vars[arg_pos]

        # NullConstant does not have conditions
        if isinstance(val, (NullConstant, Function)):
            return
        
        is_sink = ConditionManager.instance().is_sink(api_call)
        is_init = ConditionManager.instance().is_init(api_call, arg_pos)
        is_set = ConditionManager.instance().is_set(api_call, arg_pos)

        self.update_var(val, cond, is_ret, is_sink, is_init, is_set)
    # the return structure (buff_var, dynamic_buff, fix_buff)
    # dynamic_buff - list of dynamic allocated buffer
    # fix_buff - list of fixed size buffer
    def get_fixed_and_dynamic_buffers(self) -> Tuple[List[Buffer],List[Buffer]]:

        dyn_buff = []
        fix_buff = []
        
        var_buff = set()

        # dynamic arrays and respective var_len variables
        for var, cond in self.var_to_cond.items():
            if cond.len_depends_on is not None:
                var_len = cond.len_depends_on
                for x in [var, var_len]:
                    buff = None
                    if isinstance(x, Address):
                        buff = x.get_variable().get_buffer()
                    elif isinstance(x, Variable):
                        buff = x.get_buffer()
                    # Constant Values are not buffers
                    elif isinstance(x, Constant):
                        continue
                    else:
                        raise Exception(f"{x} did not expected here!")

                    if x == var:
                        dyn_buff += [buff]
                    if x == var_len:
                        var_buff.add(buff)
                        

        # fixed size arrays
        for x in self.buffs_alive:
            t = x.get_type()

            if isinstance(t, PointerType) and t.get_base_type().is_incomplete:
                continue

            if (isinstance(t, PointerType) and t.is_incomplete and
                t.get_base_type().tag == TypeTag.STRUCT):
                continue

            if t.is_incomplete:
                continue
            
            if t == self.stub_void:
                continue

            if x in set(dyn_buff).union(var_buff):
                continue

            # if t.is_const:
            #     continue
            
            if x.get_alloctype() in [AllocType.HEAP, AllocType.GLOBAL]:
                continue

            # TODO: check if the ats allow to generate an object
            if (isinstance(t, PointerType)  and 
                t.get_base_type().tag == TypeTag.STRUCT and 
                not DataLayout.instance().is_fuzz_friendly(t.get_base_type().token)):
                # if "vpx_codec_dec_cfg_t" in t.token:
                #     # continue
                #     print(f"{t} is not fuzz friendly")
                #     from IPython import embed; import traceback; embed(); exit(1)
                #     # raise ConditionUnsat()
                continue

            fix_buff += [x]

        return dyn_buff, fix_buff
    

    def generate_auxiliary_operations(self):
        buff_init = []
        counter_size = []

        dyn_byff, fix_buff = self.get_fixed_and_dynamic_buffers()

        # print("generate_buffer_init")
        # from IPython import embed; embed(); exit(1)

        for x in fix_buff:
            t = x.get_type()
            buff_init += [BuffInit(x)]

            if t.get_token() in DataLayout.string_types:
                buff_init += [SetStringNull(x)]

        for buff in dyn_byff:
            # print("generate_buffer_init -- dyn_byff")
            # from IPython import embed; embed(); exit(1)

            v = buff[0]
            c = self.var_to_cond[v]
            len_var = c.len_depends_on

            # len_var = buff_len[0]

            if buff in self.file_path_buffers:
                buff_init += [FileInit(buff, len_var)]
            # elif buff.get_token() in DataLayout.string_types:
            elif DataLayout.is_ptr_level(buff.get_type(), 1):
                buff_init += [DynArrayInit(buff, len_var)]
                if buff.get_type().get_token() in DataLayout.string_types:
                    buff_init += [SetStringNull(buff, len_var)]
            elif DataLayout.is_ptr_level(buff.get_type(), 2):
                # print("handle double pointers")
                # from IPython import embed; embed(); exit(1)
                buff_init += [DynDblArrInit(buff, len_var)]

        counter_size = []

        # dyn_buff, _ = self.get_fixed_and_dynamic_buffers()

        for init in buff_init:
            if (isinstance(init, FileInit) or 
                isinstance(init, DynArrayInit)):
                len_var = init.get_len_var()
                len_buff = len_var.get_buffer()
                counter_size += [len_buff.get_allocated_size()/8]
            elif isinstance(init, DynDblArrInit):
                len_var = init.get_len_var()
                if isinstance(len_var, Constant):
                    n_element = len_var.get_value()
                    one_cnt_size = len_var.type.get_size()
                else:
                    len_buff = len_var.get_buffer()
                    buff = init.get_buffer()
                    one_cnt_size = len_buff.get_allocated_size()
                    n_element = buff.get_number_elements()
                
                counter_size += [one_cnt_size/8] * n_element

        self.auxiliary_operations_set = True
        self.buff_init = buff_init
        self.counter_size = counter_size

    def generate_buffer_init(self) -> List[Statement]:
        if not self.auxiliary_operations_set:
            raise ("auxiliary_operations_set False, try generate_auxiliary_operations")
        return self.buff_init
    
    def get_counter_size(self):
        if not self.auxiliary_operations_set:
            raise ("auxiliary_operations_set False, try generate_auxiliary_operations")
        return self.counter_size

    def generate_buffer_decl(self) -> List[Statement]:
        buff_decl = []

        for x in self.buffs_alive:
            if x.get_type() == self.stub_void:
                continue

            if x[0] in self.const_strings:
                x_val = self.const_strings[x[0]]
                buff_decl += [ConstStringDecl(x, x_val)]
            else:
                buff_decl += [BuffDecl(x)]
            
        return buff_decl

    def get_allocated_size(self):

        _, fix_buff = self.get_fixed_and_dynamic_buffers()

        tot = sum([ b.get_allocated_size() for b in fix_buff ])

        return tot

    def generate_clean_up(self):
        clean_up = []

        for b in self.buffs_alive: # type: ignore
            # if b.get_type().is_const:
            #     continue

            if b.get_alloctype() == AllocType.HEAP:
                cm = ConditionManager.instance().find_cleanup_method(b)
                if DataLayout.is_ptr_level(b.get_type(), 2):
                    clean_up += [CleanDblBuffer(b, cm)]
                else:
                    clean_up += [CleanBuffer(b, cm)]

            if b.get_alloctype() == AllocType.STACK:
                cm = ConditionManager.instance().find_cleanup_method(b, "")
                if cm != "":
                    clean_up += [CleanBuffer(b, cm)]

        return clean_up

    def __copy__(self):
        raise Exception("__copy__ not implemented")
        
class ConditionUnsat(Exception):
    """ConditionUnsat, can't find a suitable variable in the RunningContext"""
    def __init__(self, ctx):
        self.ctx = ctx
