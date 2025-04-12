from typing import Set, Dict, List, Tuple

from driver.ir import Type, ApiCall, Buffer, PointerType, TypeTag
from driver.factory import Factory

from common import Api, FunctionConditionsSet, ValueMetadata, Access
from common import FunctionConditionsSet, DataLayout

class ConditionManager:
    sink_map            : Dict[Type, Api]
    sinks               : Set[Api]
    api_list            : Set[Api]
    init_per_type       : Dict[Type, List[Tuple[Api, int]]]
    set_per_type        : Dict[Type, List[Tuple[Api, int]]]
    source_per_type     : Dict[Type, List[Tuple[Api, int]]]
    conditions          : FunctionConditionsSet

    _instance           : "ConditionManager" = None

    def __init__(self):
        raise Exception("ConditionManager can be obtained through instance() class method")

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance
    
    def setup(self, api_list: Set[Api], api_list_all: Set[Api],
              conditions: FunctionConditionsSet):
        
        self.api_list = api_list
        self.api_list_all = api_list_all
        self.conditions = conditions

        self.init_sinks()
        self.init_source()
        self.init_init()
        self.init_source_per_type()

    # this gets ALL the sources for any custom type, not just the ones for
    # starting a driver
    def init_source_per_type(self):
    
        source_per_type = {}
    
        for api in self.api_list:

            # NOTE: some sinks could be misclassifed as source apis
            if api in self.sinks:
                continue

            ret_type = api.return_info
            the_type = Factory.normalize_type(ret_type.type, ret_type.size, 
                                              ret_type.flag, ret_type.is_const)
            the_type_orig = the_type

            if isinstance(the_type, PointerType):
                the_type = the_type.get_base_type()

            if (isinstance(the_type_orig, PointerType) and
                the_type.get_tag() == TypeTag.STRUCT):
                src_set = source_per_type.get(the_type, set())
                src_set.add(api)
                source_per_type[the_type] = src_set

        # print("check source_per_type")
        # from IPython import embed; embed(); exit(1)

        self.source_per_type = source_per_type

    def init_sinks(self):
        # sink map that links Type <=> (Sink)Api
        sink_map = {}
        sinks = set()

        get_cond = lambda x: self.conditions.get_function_conditions(
            x.function_name)

        for api in self.api_list_all:
            
            # if api.function_name == "gzclose_r":
            #     print(f"check {api.function_name} as sink")
            #     from IPython import embed; embed(); exit()
            
            fun_cond = get_cond(api)
            if (len(api.arguments_info) == 1 and 
                self.is_return_sink(api.return_info.type) and
                self.is_a_sink_condition(fun_cond.argument_at[0])):
                arg = api.arguments_info[0]
                the_type = Factory.normalize_type(arg.type, arg.size, 
                                                  arg.flag, arg.is_const)
                sink_map[the_type] = api
                sinks.add(api)

        # print("init_sinks")
        # from IPython import embed; embed(); exit()

        self.sink_map = sink_map
        self.sinks = sinks

    def is_return_sink(self, token_type: str):
        if token_type == "void":
            return True
        
        if token_type == "int":
            return True
        
        if DataLayout.instance().is_enum_type(token_type):
            return True

        return False

    def is_sink(self, api_call: ApiCall) -> bool:
        return api_call.original_api in self.sinks
    
    def get_sink_api(self) -> Set[Api]:
        return self.sinks

    def is_a_sink_condition(self, cond: ValueMetadata) -> bool:
        deletes_root = any([c.access == Access.DELETE and c.fields == [] 
                            for c in cond.ats])
        creates_root = any([c.access == Access.CREATE and c.fields == [] 
                            for c in cond.ats])
        return deletes_root and not creates_root    
    
    def find_cleanup_method(self, buff: Buffer, default: str = "free"):

        buff_type = buff.get_type()

        if buff_type not in self.sink_map:
            return default
        
        api_sink = self.sink_map[buff_type]
        return api_sink.function_name

    def is_source(self, cond: ValueMetadata):
        return (len([at for at in cond.ats
                if at.access == Access.CREATE and at.fields == []]) != 0)
    
    def get_source_api(self) -> Set[Api]:
        return self.source_api

    def init_source(self) -> Set[Api]:

        source_api = set()

        # get_cond = lambda x: self.conditions.get_function_conditions(
        #     x.function_name)

        for api in self.api_list:
            # if DataLayout.instance().has_incomplete_type():
            #     if (not any(arg.is_type_incomplete for arg in api.arguments_info) 
            #         and api.return_info.is_type_incomplete):
            #         source_api.add(api)
            #     if (not any(arg.is_type_incomplete for arg in api.arguments_info) 
            #         and api.return_info.type == "void*"):
            #         source_api.add(api)
            # else:
            #     source_api.add(api)

            # if api.function_name == "bstr_builder_create":
            #     print("get_source_api")
            #     from IPython import embed; embed(); exit(1)

            # NOTE: some sinks could be misclassifed as source apis
            if api in self.sinks:
                continue

            # fun_cond = get_cond(api)

            # if api.function_name == "cJSON_ParseWithOpts":
            #     print(f"get_source_api {api.function_name}")
            #     from IPython import embed; embed(); exit(1)

            num_arg_ok = 0
            for arg in api.arguments_info:
                the_type = Factory.normalize_type(arg.type, arg.size, arg.flag, arg.is_const)
                the_type_orig = the_type
                # arg_cond = fun_cond.argument_at[arg_p]
                if isinstance(the_type, PointerType):
                    the_type = the_type.get_base_type()
                tkn = the_type.token
                if DataLayout.instance().is_primitive_type(tkn):
                    num_arg_ok += 1 
                elif DataLayout.instance().has_user_define_init(tkn):
                    num_arg_ok += 1 
                elif DataLayout.instance().is_enum_type(tkn):
                    num_arg_ok += 1
                elif (not the_type.is_incomplete and 
                      DataLayout.instance().is_fuzz_friendly(tkn)):
                    num_arg_ok += 1
                elif DataLayout.is_ptr_level(the_type_orig, 2):
                    num_arg_ok += 1 
                # elif (the_type.tag == TypeTag.STRUCT and
                #       DataLayout.instance().is_fuzz_friendly(tkn) and
                #       Conditions.is_unconstraint(arg_cond)):
                #     num_arg_ok += 1


            # I can initialize all the arguments
            if len(api.arguments_info) == num_arg_ok:
                source_api.add(api)

        # print("get_source_api")
        # from IPython import embed; embed(); exit(1)


        # FLAVIO: this is supposed to handle cases where a type T is alias of void* AND a function allocates new T
        custom_voidp_source = False
        for api in source_api:
            cond = self.conditions.get_function_conditions(api.function_name).return_at
            if self.is_source(cond) and api.return_info.type == "void *":
                custom_voidp_source = True

        if custom_voidp_source:
            new_source = []
            for api in source_api:
                if all([a.type != "void *" for a in api.arguments_info]):
                    new_source.append(api)
            source_api = new_source

        self.custom_voidp_source = custom_voidp_source

        self.source_api = source_api

    def init_init(self):
        #  api_call: ApiCall, api_cond: FunctionConditions, 
                    # arg_pos: int):
        
        # api_name = api_call.function_name
        # if api_name == "aom_codec_decode" and arg_pos == 0:
        #     print("is_init_api")
        #     from IPython import embed; embed(); exit(1)

        init_per_type = {}
        set_per_type = {}

        get_cond = lambda x: self.conditions.get_function_conditions(
            x.function_name)
        to_api = lambda x: Factory.api_to_apicall(x)

        for api in self.api_list:
            api_cond = get_cond(api)
            api_call = to_api(api)
            
            for arg_pos, arg_type in enumerate(api_call.arg_types):
                cond = api_cond.argument_at[arg_pos] 

                if len(cond.setby_dependencies) == 0:
                    continue

                arg_ok = 0     
                n_incomplete_type = 0
                for d in cond.setby_dependencies:
                    p_idx = int(d.replace("param_", ""))
                    d_type = api_call.arg_types[p_idx]
                    
                    tt = d_type
                    if isinstance(d_type, PointerType):
                        tt = d_type.get_base_type()

                    if tt.tag == TypeTag.STRUCT:
                        token = tt.get_token()
                        if DataLayout.instance().is_fuzz_friendly(token):
                            arg_ok += 1
                        elif tt.is_incomplete:
                            n_incomplete_type += 1
                    elif tt.tag == TypeTag.PRIMITIVE:
                        arg_ok += 1

                if (arg_ok == len(cond.setby_dependencies) - 1 and 
                    n_incomplete_type == 1):
                    xx = init_per_type.get(arg_type, set())
                    xx.add((api, arg_pos))
                    init_per_type[arg_type] = xx
                else:
                    xx = set_per_type.get(arg_type, set())
                    xx.add((api, arg_pos))
                    set_per_type[arg_type] = xx

        # print("check init_init")
        # from IPython import embed; embed(); exit(1)

        self.init_per_type = init_per_type
        self.set_per_type = set_per_type
        
        # set_init = self.get_init_api()
        setby_set = set()
        
        # init_per_type       : Dict[Type, List[Tuple[Api, int]]]
        for _, l_api_pos in self.set_per_type.items():
            if len(l_api_pos) > 1:
                for api, _ in l_api_pos:
                    setby_set.add(api)
        
        for a in setby_set:
            if a in self.source_api:
                self.source_api.remove(a)
               
        # print("clean wrong sources")
        # from IPython import embed; embed(); exit()

    def get_sink_api(self) -> Set[Api]:
        return self.sinks
    
    def get_init_api(self) -> Set[Api]:
        init_set = set()
        
        # init_per_type       : Dict[Type, List[Tuple[Api, int]]]
        for _, l_api_pos in self.init_per_type.items():
            for api, _ in l_api_pos:
                init_set.add(api)

        return init_set
    
    # def has_init_api(self, type: Type) -> bool:
    #     return type in self.init_per_type

    def has_source(self, type: Type) -> bool:
        return type in self.source_per_type
    
    def needs_init_or_setby(self, type: Type) -> bool:
        if type in self.init_per_type:
            return True
        
        # if type in self.set_per_type:
        #     ss = self.set_per_type[type]
        #     return len(ss) == 1
                
        return False
    
    def is_setby(self, api_call: ApiCall, arg_pos: int) -> bool:
        if arg_pos < 0:
            return False
        
        arg_type = api_call.arg_types[arg_pos]
        api = api_call.original_api

        # this filters out wrong init types that must be actually initialized
        # through a source
        if arg_type is self.source_per_type:
            return False

        if arg_type not in self.set_per_type:
            return False

        setby_list = self.set_per_type[arg_type]

        return (api, arg_pos) in setby_list and len(setby_list) == 1
    
    def is_init(self, api_call: ApiCall, arg_pos: int) -> bool:
        if arg_pos < 0:
            return False
        
        arg_type = api_call.arg_types[arg_pos]
        api = api_call.original_api

        # this filters out wrong init types that must be actually initialized
        # through a source
        if arg_type is self.source_per_type:
            return False

        if arg_type not in self.init_per_type:
            return False

        init_list = self.init_per_type[arg_type]

        return (api, arg_pos) in init_list
    
    def is_set(self, api_call: ApiCall, arg_pos: int) -> bool:
        if arg_pos < 0:
            return False
        
        arg_type = api_call.arg_types[arg_pos]
        api = api_call.original_api

        if arg_type not in self.set_per_type:
            return False

        set_list = self.set_per_type[arg_type]

        return (api, arg_pos) in set_list