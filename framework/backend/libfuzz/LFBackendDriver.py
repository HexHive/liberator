from driver import Driver
from driver.ir import ApiCall, BuffDecl, BuffInit, FileInit, AllocType
from driver.ir import PointerType, Address, Variable, Type, DynArrayInit
from driver.ir import Statement, Value, NullConstant, ConstStringDecl
from driver.ir import AssertNull, CleanBuffer, SetNull, SetStringNull, Function
from driver.ir import DynDblArrInit, CleanDblBuffer, Constant
from backend import BackendDriver
from common import DataLayout

import random, string, os, shutil

from typing import List, Set, Dict, Tuple, Optional

class LFBackendDriver(BackendDriver):

    def __init__(self, working_dir, seeds_dir, num_seeds, headers_dir, public_headers):
        self.working_dir = working_dir
        self.seeds_dir   = seeds_dir
        self.headers_dir = headers_dir
        self.num_seeds = num_seeds
        self._idx = 0

        public_headers_lst = set()
        with open(public_headers, 'r') as ph:
            for l in ph:
                l = l.strip()
                if l:
                    public_headers_lst.add(l)

        self.file_pointer_cnt = 0

        self.seed_clean_up = False

        self.headers = [] # os.listdir(headers_dir)
        for root, _, f_names in os.walk(headers_dir):
            for f in f_names:
                if ((f.endswith(".h") or f.endswith(".h++") or 
                    f.endswith(".hpp") or f.endswith(".hxx")) and
                    f in public_headers_lst):
                    f_full = os.path.join(root, f)
                    f_rel = os.path.relpath(f_full, headers_dir)
                    # from IPython import embed; embed(); exit(1)
                    self.headers.append(f_rel)

    def get_name(self) -> str:
        m_idx = self._idx 
        self._idx = self._idx + 1

        file_name = f"driver{m_idx}.cc"

        return file_name

    def emit_seeds(self, driver, driver_filename: str):

        # hack to remove extension!
        if "." in driver_filename:
            ext_pos = driver_filename.find(".")
            driver_filename = driver_filename[:ext_pos]

        seed_folder = os.path.join(self.seeds_dir, driver_filename)

        # clean previous seeds
        shutil.rmtree(seed_folder, ignore_errors=True)
        os.mkdir(seed_folder)

        # seed size in bytes
        seed_size = driver.get_input_size()

        counter_size = driver.get_counter_size()
        seed_fix_size = driver.get_input_size()
        
        for x in range(1, self.num_seeds + 1):
            with open(os.path.join(seed_folder, f"seed{x}.bin"), "wb") as f:

                # fix part of the seed
                complete_seed_buffer = os.urandom(seed_fix_size)
                # TVL part of the seed
                for c in counter_size:
                    # I want 10 bytes for buffers at the beginning
                    dyn_buff_len = 10
                    # maybe I watn a random range of bytes?
                    # dyn_buff_len = os.getrandom(10)
                    dyn_buff_len_bytes = dyn_buff_len.to_bytes(c, 'little')
                    buff_initial_bytes = os.getrandom(dyn_buff_len)
                    complete_seed_buffer += (dyn_buff_len_bytes + 
                                             buff_initial_bytes)
                    
                    # print("about to write a seed")
                    # from IPython import embed; embed(); exit(1)

                # f.write(os.urandom(seed_size))
                f.write(complete_seed_buffer)

    def emit_stub_functions(self, stub_functions: List[Function]) -> str:
        stubs = ""

        # print("emit_stub_functions")
        # from IPython import embed; embed(); exit(1)

        for _, f in stub_functions.items():
            f_name = f.token
            f_return = f.ret_type
            f_arguments = f.arg_types

            stubs += f"{f_return} {f_name} {f_arguments} {{\n"
            if f_return != "void":
                stubs += f"\treturn ({f_return})0;\n"
            stubs += "}\n"
            stubs += "\n"

        return stubs

    def emit_defines(self, seed_fix_size, counter_size) -> str:

        counter_size_str = ",".join([f"{c}" for c in counter_size])
        min_seed_size = seed_fix_size + sum(counter_size)

        cm = ""
        cm += f"#define FIXED_SIZE {seed_fix_size}\n"
        cm += f"#define COUNTER_NUMBER {len(counter_size)}\n"
        cm += f"#define MIN_SEED_SIZE {min_seed_size}\n"

        cm += f"const unsigned counter_size[COUNTER_NUMBER] = "
        cm += f"{{ {counter_size_str} }};\n"

        cm += "\n#define NEW_DATA_LEN 4096\n\n"
        
        cm += "\n#define MIN(x,y) ((x < y) ? x : y)\n\n"

        return cm
    
    last_stmt = None

    def emit_driver(self, driver: Driver, driver_filename: str):

        self.seed_clean_up = len(driver.clean_up_sec) != 0
        self.has_counter = len(driver.get_counter_size()) != 0

        seed_fix_size = driver.get_input_size()
        counter_size = driver.get_counter_size()
        stub_functions = driver.get_stub_functions()
        
        LFBackendDriver.drv = driver

        with open(os.path.join(self.working_dir, driver_filename), "w") as f:
            # TODO: add headers inclusion
            for header in self.headers:
                f.write(f"#include <{header}>\n")

            f.write("\n")
            f.write("#include <string.h>\n")
            f.write("#include <stdlib.h>\n")
            f.write("#include <stdio.h>\n")
            f.write("#include <time.h>\n")
            f.write("#include <stdint.h>\n")

            # if self.has_counter:
            f.write("\n")
            f.write(self.emit_defines(seed_fix_size, counter_size))

            # callback functions
            if len(stub_functions) != 0:
                f.write("\n")
                f.write(self.emit_stub_functions(stub_functions))

            f.write("\n")

            f.write("extern \"C\" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t Size) {\n")

            # if self.has_counter:
            f.write("\tif (Size < MIN_SEED_SIZE) return 0;\n")

            # for stmt in stmt_instances:
            for stmt in driver:
                f.write("\t" + self.stmt_emit(stmt) + "\n")

            if self.seed_clean_up:
                f.write("\nclean_up:\n")

            for stmt in driver.clean_up_sec:
                f.write("\t" + self.stmt_emit(stmt) + "\n")

            f.write("\n\treturn 0;\n}")

            if self.has_counter:
                f.write("\n\n")
                f.write(self.inject_custom_mutator())

        # print(driver.get_input_size())

        # return driver_filename

    def inject_custom_mutator(self) -> str:

        cm = ""
        cm += "int cmpfunc (const void * a, const void * b)\n"
        cm += "{return ( *(unsigned*)a - *(unsigned*)b );}\n\n"

        cm += "// Forward-declare the libFuzzer's mutator callback.\n"
        cm += "extern \"C\" size_t LLVMFuzzerMutate(uint8_t *Data, size_t Size, size_t MaxSize);\n\n"

        cm += "extern \"C\" size_t LLVMFuzzerCustomMutator(uint8_t *Data, size_t Size, size_t MaxSize, unsigned int Seed) {\n\n"

        cm += "\t// select the field to mutate: fized or a dynamic one\n"
        cm += "\tunsigned field = (unsigned)(rand() % (COUNTER_NUMBER + 1));\n"

        cm += "\t// mutate the fixed part\n"
        cm += "\tif (field == 0) {\n"

        cm += "\t\tuint8_t fixed_field[FIXED_SIZE];\n"
        cm += "\t\tmemcpy(fixed_field, Data, FIXED_SIZE);\n"

        cm += "\t\tsize_t new_fixed_data = LLVMFuzzerMutate(fixed_field, FIXED_SIZE, FIXED_SIZE);\n\n"

        cm += "\t\tif (new_fixed_data > FIXED_SIZE) {\n"
        cm += "\t\t\tprintf(\"[ERROR] for the fixed size, I have a longer size\");\n"
        cm += "\t\t\texit(1);\n"
        cm += "\t\t}\n"

        cm += "\t\t// LLVMFuzzerMutate could reduce the seed size\n"
        cm += "\t\tif (new_fixed_data < FIXED_SIZE) {\n"
        cm += "\t\t\tsize_t to_append_size = FIXED_SIZE-new_fixed_data;\n"
        cm += "\t\t\tfor (unsigned i = 0; i < to_append_size; i++)\n"
        cm += "\t\t\t// fixed_field[new_fixed_data+i] = (uint8_t)rand();\n"
        cm += "\t\t\tfixed_field[new_fixed_data+i] = 0x0;\n"
        cm += "\t\t}\n"

        cm += "\t\tmemcpy(Data, fixed_field, FIXED_SIZE);\n"

        cm += "\t\treturn Size;\n"

        cm += "\t// mutate one of the dynamic fields\n"
        cm += "\t} else {\n"
        cm += "\t\tunsigned dyn_field_idx = field - 1;\n\n"

        cm += "\t\tsize_t counter = 0;\n"
        cm += "\t\tuint8_t *counter_addr = Data + FIXED_SIZE;\n"
        cm += "\t\tuint8_t *buffer_start, *buffer_end;\n"

        cm += "\t\tsize_t to_read = MIN(sizeof(size_t), counter_size[0]);\n"
        cm += "\t\tmemcpy(&counter, counter_addr, to_read);\n"
        cm += "\t\tbuffer_start = Data + FIXED_SIZE + counter_size[0];\n"
        cm += "\t\tbuffer_end = buffer_start + counter;\n"

        cm += "\t\tif (dyn_field_idx != 0) {\n"

        cm += "\t\t\tfor (unsigned i = 1; i < COUNTER_NUMBER && i != (dyn_field_idx + 1); i++) {\n"
        cm += "\t\t\t\tto_read = MIN(sizeof(size_t), counter_size[i]);\n"
        cm += "\t\t\t\tmemcpy(&counter, buffer_end, to_read);\n"

        cm += "\t\t\t\tcounter_addr = buffer_end;\n"
        cm += "\t\t\t\tbuffer_start = buffer_end + counter_size[i];\n"
        cm += "\t\t\t\tbuffer_end = buffer_start + counter;\n\n"
                    
        cm += "\t\t\t}\n"
        cm += "\t\t}\n"

        cm += "\t\tuint8_t dynamic_field[NEW_DATA_LEN];\n\n"

        cm += "\t\tmemcpy(dynamic_field, buffer_start, counter);\n\n"

        cm += "\t\tsize_t new_dynamic_data = LLVMFuzzerMutate(dynamic_field, counter, NEW_DATA_LEN);\n\n"

        cm += "\t\tif (new_dynamic_data > NEW_DATA_LEN) {\n"
        cm += "\t\t\tprintf(\"[ERROR] for the dynamic size, I have a longer size\");\n"
        cm += "\t\t\texit(1);\n"
        cm += "\t\t}\n\n"

        cm += "\t\tsize_t new_whole_data_size = Size - (counter - new_dynamic_data);\n"
        cm += "\t\tif (new_whole_data_size == 0 || new_whole_data_size > MaxSize)\n"
        cm += "\t\t\treturn 0;\n\n"

        cm += "\t\tuint8_t *new_data = (uint8_t*)malloc(new_whole_data_size);\n"
        cm += "\t\tuint8_t *new_data_original = new_data;\n"
        cm += "\t\tmemset(new_data, 0, new_whole_data_size);\n\n"

        cm += "\t\t// copy what stays before the old dyn buffer\n"
        cm += "\t\tmemcpy(new_data, Data, counter_addr - Data);\n"
        cm += "\t\tnew_data += counter_addr - Data;\n\n"

        cm += "\t\t// store the new counter\n"
        cm += "\t\tsize_t real_counter_size = MIN(sizeof(size_t), counter_size[dyn_field_idx]);\n"
        cm += "\t\tmemcpy(new_data, &new_dynamic_data, real_counter_size);\n"
        cm += "\t\tnew_data += counter_size[dyn_field_idx];\n\n"

        cm += "\t\t// store the new dynamic field\n"
        cm += "\t\tmemcpy(new_data, dynamic_field, new_dynamic_data);\n"
        cm += "\t\tnew_data += new_dynamic_data;\n\n"

        cm += "\t\t// dynamic region is not the last one\n"
        cm += "\t\tif (buffer_end != Data + Size && new_dynamic_data > 0) {\n"
        cm += "\t\t\tsize_t leftover_size = (Data + Size) - buffer_end;\n"
        cm += "\t\t\tmemcpy(new_data, buffer_end, leftover_size);\n"
        cm += "\t\t}\n\n"

        cm += "\t\t// re-transfer the new seed into the Data buffer\n"
        cm += "\t\tmemcpy(Data, new_data_original, new_whole_data_size);\n"
        cm += "\t\tfree(new_data_original);\n\n"

        cm += "\t\treturn new_whole_data_size;\n"
        cm += "\t}\n"

        cm += "}\n"

        return cm

    # Address
    def address_emit(self, address: Address, depth: int = -1) -> str:
        variable = address.variable
        type = variable.get_type()
        buffer  = variable.get_buffer()
        token   = self.clean_token(buffer.token)

        # if type.token == "char*":
        #     print("token char*")
        #     from IPython import embed; embed(); exit(1)

        if isinstance(type, PointerType):
            # idx     = variable.get_index()
            if buffer.get_alloctype() in [AllocType.HEAP, AllocType.GLOBAL]:
                return f"{self.variable_emit(variable, depth)}"
            else:
                return f"{token}"
        else:
            return f"&{self.variable_emit(variable)}"

    def stmt_emit(self, stmt: Statement) -> str:
        if isinstance(stmt, BuffDecl):
            return self.buffdecl_emit(stmt)
        if isinstance(stmt, ConstStringDecl):
            return self.conststringdecl_emit(stmt)
        elif isinstance(stmt, BuffInit):
            return self.buffinit_emit(stmt)
        elif isinstance(stmt, FileInit):
            return self.fileinit_emit(stmt)
        elif isinstance(stmt, DynArrayInit):
            return self.dynarrayinit_emit(stmt)
        elif isinstance(stmt, ApiCall):
            return self.apicall_emit(stmt)
        elif isinstance(stmt, AssertNull):
            return self.assertnull_emit(stmt)
        elif isinstance(stmt, CleanBuffer):
            return self.cleanbuffer_emit(stmt)
        elif isinstance(stmt, SetNull):
            return self.setnull_emit(stmt)
        elif isinstance(stmt, SetStringNull):
            return self.setstringnull_emit(stmt)
        elif isinstance(stmt, DynDblArrInit):
            return self.dyndblarrinit_emit(stmt)
        elif isinstance(stmt, CleanDblBuffer):
            return self.cleandblbuffer_emit(stmt)
        raise NotImplementedError
    
    def cleandblbuffer_emit(self, stmt: CleanDblBuffer) -> str:
        buff            = stmt.get_buffer()
        cleanup_method  = stmt.get_cleanup_method()
        buff_nelem      = buff.get_number_elements()
        buff_type       = buff.get_type()

        # v = self.value_emit(buff[0])

        # NOTE: this is super ugly but not sure how to do otherwise
        # num_extra_brackets = buff.type.token.count("*")-1
        # print("cleanbuffer_emit")
        # from IPython import embed; embed(); exit(1)

        # extra_brackets = "[0]" * num_extra_brackets

        # NOTE: remove "const" adjustments
        cast_str = ""
        # if "const" in buff_type.token:
        #     pointee_type_token = buff_type.get_pointee_type().token
        #     pointee_type_token = pointee_type_token.replace(" const", "")
        #     cast_str = f"({pointee_type_token})"

        buff_i = f"{self.value_emit(buff[0])}[i]"

        # add a shadow copy for the array
        x_idx = 0
        x_token = self.clean_token(buff.get_token()) + "_shadow"
        x_value = f"{x_token}[{x_idx}][i]"

        str = "//clean dbl array\n"
        # str += f"\tfor (uint i = 0; i < {buff_nelem}; i++) "
        # str += f" if ({buff_i} != 0 && {x_value} == {buff_i} ) "
        # str += f"{cleanup_method}({cast_str}{buff_i});\n"
        str += f"\tfor (uint i = 0; i < {buff_nelem}; i++) "
        str += f" if ({x_value} != 0 )"
        str += f" {cleanup_method}({cast_str}{x_value});\n"

        return str


    # DynDblArrInit
    def dyndblarrinit_emit(self, stmt: DynDblArrInit) -> str:
        var_len = stmt.get_len_var()
        buff = stmt.get_buffer()

        # buff_token = self.clean_token(buff.get_token())
        buff_nelem = buff.get_number_elements()

        buff_type = buff.get_type()
        tkn_base = buff_type.get_pointee_type().get_token()

        var_len_init = BuffInit(var_len.get_buffer())
        dst_type = self.type_emit(buff_type)

        buff_i = f"{self.value_emit(buff[0])}[i]"
        var_lel_val = self.value_emit(var_len)

        # print("dyndblarrinit_emit")
        # from IPython import embed; embed(); exit(1)

        # NOTE: remove "const" adjustment
        cast_str = ""
        is_const = False
        # if "const" in buff_type.token:
        #     pointee_type_token = buff_type.get_pointee_type().token
        #     pointee_type_token = pointee_type_token.replace(" const", "")
        #     cast_str = f"({pointee_type_token})"
        #     tkn_base = tkn_base.replace(" const", "")
        #     is_const = True

        str = "//dyn dbl array init\n"
        str += f"\tfor (uint i = 0; i < {buff_nelem}; i++) {{\n"
        
        x_elm_size = ""
        if not buff_type.get_pointee_type().is_incomplete:
            x_elm_size = f"*sizeof({buff_i}[0])"
        else:
            raise Exception(f"sizeof({buff_i}) is incomplete in dyndblarrinit_emit!")
        
        # var_len from fuzzer seed
        str += "\t\t" + self.buffinit_emit(var_len_init) + "\n"
        # malloc
        str += f"\t\t{buff_i} = ({dst_type}*)malloc({self.value_emit(var_len)}{x_elm_size});\n"

        # add a shadow copy for the array
        x_idx = 0
        x_token = self.clean_token(buff.get_token()) + "_shadow"
        x_value = f"{x_token}[{x_idx}][i]"

        str += f"\t\t{x_value} = {buff_i};\n"

        # memcpy
        str += f"\t\tmemcpy({cast_str}{buff_i}, data, {self.value_emit(var_len)});\n"
        if tkn_base in DataLayout.string_types:
            # set NULL-pointer strings
            if is_const:
                # char* xx = (char*)charconst_pp_h0[0][i];
                str += f"\t\t{tkn_base} xx = {cast_str}{buff_i};\n"
                # xx[int_s0[0] - 1] = 0;
                str += f"\t\txx[{var_lel_val} - 1] = 0;\n"
            else:
                str += f"\t\t{buff_i}[{var_lel_val} - 1] = 0;\n"
        # move cursor ahead
        str += f"\t\tdata += {self.value_emit(var_len)};\n"

        str += "\t}\n"

        return str

    # SetStringNull
    def setstringnull_emit(self, stmt: SetStringNull) -> str:
        buff = stmt.get_buffer()
        len_var = stmt.get_len_var()

        v = self.address_emit(buff.get_address())
        if len_var is None:
            return f"{v}[sizeof({v}) - 1] = 0;"
        else:
            l = self.value_emit(len_var)
            null_ckeck = f"if ({l} > 0) "
            return f"{null_ckeck}{v}[{l} - 1] = 0;"


    # SetNull
    def setnull_emit(self, setnull: SetNull) -> str:
        buff = setnull.get_buffer()
        
        depth = DataLayout.get_ptr_level(buff.get_type()) - 1
        v = self.value_emit(buff[0], depth)

        shadow_update = ""
        if buff.get_alloctype() == AllocType.HEAP:
            x_idx = 0
            # x_token = self.clean_token(buff.get_token()) + "_shadow"
            # x_value = f"{x_token}[{x_idx}][i]"            
            x_token = self.clean_token(buff.get_token()) + "_shadow"
            # from IPython import embed; embed(); exit(1)
            x_value = f"{x_token}[{x_idx}]"
            if depth > 0:
                x_value += "[0]"
            shadow_update = f"\n\t{x_value} = 0;"

        # print("setnull_emit")
        # from IPython import embed; embed(); exit(1)

        return f"{v} = 0;{shadow_update}"

    # CleanBuffer
    def cleanbuffer_emit(self, cleanbuffer: CleanBuffer) -> str:
        buff            = cleanbuffer.get_buffer()
        cleanup_method  = cleanbuffer.get_cleanup_method()

        v = self.value_emit(buff[0])

        # NOTE: this is super ugly but not sure how to do otherwise
        num_extra_brackets = buff.type.token.count("*")-1

        extra_brackets = "[0]" * num_extra_brackets

        # buffers in stack and heap have different handling
        if buff.alloctype == AllocType.STACK:
            v_stack = self.clean_token(buff.token)
            return f"{cleanup_method}({v_stack});"
        elif buff.alloctype == AllocType.HEAP:
            # print("cleanbuffer_emit 2")
            # from IPython import embed; embed(); exit(1)

            # add a shadow copy for the array
            x_idx = 0
            x_token = self.clean_token(buff.get_token()) + "_shadow"
            x_value = f"{x_token}[{x_idx}]"

            # to_ret = f"if ({v}{extra_brackets} != 0 && "
            # to_ret += f"{x_value} == {v}{extra_brackets}) "
            # to_ret += f"{cleanup_method}({v}{extra_brackets});"
            
            to_ret = f"if ({x_value} != 0)"
            # to_ret += f" {cleanup_method}({x_value});" // clean the shadow var
            to_ret += f" {cleanup_method}({v}{extra_brackets});"

            return to_ret

    # ConstStringDecl
    def conststringdecl_emit(self, cnststrdecl: ConstStringDecl) -> str:
        # NOTE: ConstStringDecl ensures to assign only [const] char* 
        buffer      = cnststrdecl.get_buffer()
        str_value   = cnststrdecl.get_string_val()

        type        = buffer.get_type()
        n_element   = buffer.get_number_elements()
        token       = self.clean_token(buffer.get_token())

        n_stars = 0
        tmp_type = type
        while isinstance(tmp_type, PointerType):
            n_stars += 1
            tmp_type = tmp_type.get_pointee_type()
        str_stars = "*"
        # n_brackets = "[1]"*(n_stars-1)
        const_attr = "const " if type.is_const else ""

        stmt = ""
        stmt += f"{const_attr}{self.type_emit(type)} "
        stmt += f"{str_stars}{token} = \"{str_value}\";"

        return stmt

    # BuffDecl
    def buffdecl_emit(self, buffdecl: BuffDecl) -> str:
        buffer      = buffdecl.get_buffer()

        type        = buffer.get_type()
        n_element   = buffer.get_number_elements()
        token       = self.clean_token(buffer.get_token())
        alloctype   = buffer.get_alloctype()

        n_stars = 0
        tmp_type = type
        while isinstance(tmp_type, PointerType):
            n_stars += 1
            tmp_type = tmp_type.get_pointee_type()

        str_stars = ""
        n_brackets = ""
        
        # if buffer in heap, add a * and remove a [1], i.e., trasform the buffer
        # in an array of pointers instead of variables
        if alloctype in [AllocType.HEAP, AllocType.GLOBAL]:
            str_stars = "*"
            n_brackets = "[1]"*(n_stars-1)

        # NOTE: all declarations are not-const!
        const_attr = ""
        # const_attr = "const " if type.is_const else ""
        # if type.token == "u_char**":
        #     const_attr = "const "

        if buffer.get_alloctype() in [AllocType.HEAP, AllocType.GLOBAL]:
            if DataLayout.is_ptr_level(type, 2):
                n_element += 1
            to_ret = f"{const_attr}{self.type_emit(type)} {str_stars}{token}{n_brackets}[{n_element}] = {{ 0 }};"

            if buffer.get_alloctype() == AllocType.HEAP:
                to_ret += "\n\t"
                to_ret += f"{const_attr}{self.type_emit(type)} {str_stars}{token}_shadow{n_brackets}[{n_element}] = {{ 0 }};"

            return to_ret
        else:
            
            decl_str = f"{const_attr}{self.type_emit(type)} {str_stars}{token}{n_brackets}[{n_element}];"
            
            type_base = type
            if isinstance(type_base, PointerType):
                type_base = type_base.get_pointee_type()
            
            # if a type is not fuzz friendly, using memset is the most compatible way to initiliaze it
            # if (DataLayout.instance().is_enum_type(type_base.get_token()) or
            #     not DataLayout.instance().is_fuzz_friendly(type_base.get_token())):
            decl_str += f"\n\tmemset({str_stars}{token}, 0x0, sizeof({str_stars}{token}));"
        
            return decl_str

    def get_new_file_pointer(self):
        cnt = self.file_pointer_cnt
        self.file_pointer_cnt += 1
        return f"p{cnt}"

    def dynarrayinit_emit(self, dynarrayinit: DynArrayInit) -> str:
        stmt = "//dyn array init\n"

        var_len = dynarrayinit.get_len_var()
        buff = dynarrayinit.get_buffer()
        
        buff_type = buff.get_type()
        dst_type = self.type_emit(buff_type)
        
        # TODO: check if this is a good idea!
        
        x_elm_size = ""
        if (isinstance(buff_type, PointerType) and 
            not buff_type.get_pointee_type().is_incomplete):
            x_elm_size = f"*sizeof({self.value_emit(buff[0])}[0])"
        else:
            raise Exception(f"sizeof({buff[0]}) is incomplete in dynarrayinit_emit!")
            

        # var_len from fuzzer seed
        var_len_init = BuffInit(var_len.get_buffer())
        stmt += "\t" + self.buffinit_emit(var_len_init) + "\n"
        # malloc
        stmt += f"\t{self.value_emit(buff[0])} = ({dst_type}*)malloc({self.value_emit(var_len)}{x_elm_size});\n"
        # add a shadow copy for the array
        x_idx = 0
        x_token = self.clean_token(buff.get_token()) + "_shadow"
        x_value = f"{x_token}[{x_idx}]"
        stmt += f"\t{x_value} = {self.value_emit(buff[0])};\n"
        # memcpy
        stmt += f"\tmemcpy({self.value_emit(buff[0])}, data, {self.value_emit(var_len)});\n"
        # move cursor ahead
        stmt += f"\tdata += {self.value_emit(var_len)};\n"

        return stmt

    # FileInit
    def fileinit_emit(self, fileinit: FileInit) -> str:
        stmt = "//file init\n"

        var_len = fileinit.get_len_var()

        # file pointer name
        p = self.get_new_file_pointer()

        # print("fileinit_emit ")
        # from IPython import embed; embed(); exit(1)

        # var_len from fuzzer seed
        var_len_init = BuffInit(var_len.get_buffer())
        stmt += "\t" + self.buffinit_emit(var_len_init) + "\n"
        # file open
        buff = fileinit.get_buffer()
        addrbuff = buff[0].get_address()
        stmt += f"\tFILE *{p} = fopen({self.value_emit(addrbuff)}, \"w\");\n"
        # fwrite into buff value
        stmt += f"\tfwrite(data, {self.value_emit(var_len)}, 1, {p});\n"
        # fclose + move cursor ahead
        stmt += f"\tfclose({p});data += {self.value_emit(var_len)};\n"

        return stmt

    # BuffInit
    def buffinit_emit(self, buffinit: BuffInit) -> str:
        buffer      = buffinit.get_buffer()

        type        = buffer.get_type()
        token       = self.clean_token(buffer.get_token())

        if type.is_incomplete:
            raise Exception(f"I can't initialize a buffer of imcomplete types {type}")
  
        return f"memcpy({token}, data, sizeof({token}));data += sizeof({token});"

    # AssertNull
    def assertnull_emit(self, assertnull: AssertNull) -> str:
        buff = assertnull.get_buffer()

        if self.seed_clean_up:
            return f"if ({self.value_emit(buff[0])} == 0) goto clean_up;"
        else:
            return f"if ({self.value_emit(buff[0])} == 0) return 0;"

    # ApiCall
    def apicall_emit(self, apicall: ApiCall) -> str:
        ret_var = apicall.ret_var
        ret_type = apicall.ret_type
        arg_vars = apicall.arg_vars
        arg_types = apicall.arg_types
        function_name = apicall.function_name
        namespace = apicall.namespace
        is_vararg = apicall.is_vararg

        if namespace is not None and len(namespace) > 0:
            function_name = "::".join(namespace) + "::" + function_name

        if is_vararg:
            for vv in apicall.vararg_var:
                arg_vars += [vv] 

        ret_var_code = self.value_emit(ret_var)

        str_vals = []
        for p, a in enumerate(arg_vars):
            # if p == 0 and apicall.function_name == "ares_free_hostent":
            #     print("apicall_emit")
            #     from IPython import embed; embed(); exit(1)
            
            if isinstance(a, Address) and p < len(arg_types):
                va = a.get_variable()
                lvl_arg = DataLayout.get_ptr_level(arg_types[p])
                lvl_var = DataLayout.get_ptr_level(va.get_type())
            else:
                lvl_arg = 0
                lvl_var = 0
                
            if lvl_var > lvl_arg:
                x = self.value_emit(a, lvl_var - lvl_arg)
            else:
                x = self.value_emit(a)
            
            
            # print("type cast?")
            # from IPython import embed; embed(); exit(1)
            
            if (p < len(arg_types) and
                self.has_some_const(arg_types[p]) and 
                not arg_types[p].to_function):
            # != va.get_type():
                # print("xxxaaa")
                # from IPython import embed; embed(); exit(1)
                cast = self.full_type_emit(arg_types[p])
                x = f"({cast}){x}"
            
            if apicall.has_max_value(p):
                m = apicall.get_max_value(p)
                str_vals += [f" ((uint){x}) % {m}"]
            else:
                str_vals += [x]

        arg_vars_code = ", ".join(str_vals)

        ret_buff = None
        if isinstance(ret_var, Address):
            ret_var_type = ret_var.get_variable().get_type()
            ret_buff = ret_var.get_variable().get_buffer()
        elif isinstance(ret_var, NullConstant):
            ret_var_type = ret_var.type
            ret_buff = None
        else:
            ret_var_type = ret_var.get_type()
            ret_buff = ret_var.get_buffer()

        if ret_var_type == Type("void"):
            return f"{function_name}({arg_vars_code});"

        # if self.function_name == "_TIFFmalloc":
        #     from IPython import embed; embed(); exit()

        cast_operator = ""
        
        # if function_name == "cJSON_Version":
        #     print("apicall_emit")
        #     from IPython import embed; embed(); exit(1)

        if ret_type != ret_var_type or self.has_some_const(ret_type):
            # type_emit = self.type_emit(ret_var_type)
            # print("Xxxx")
            # from IPython import embed; embed(); exit()
            # type_emit = self.clean_token()
            cast_operator = f"({self.full_type_emit(ret_type, False)})"

        shadow_update = ""
        if ret_buff != None and ret_buff.get_alloctype() == AllocType.HEAP:
            x_idx = 0
            # x_token = self.clean_token(buff.get_token()) + "_shadow"
            # x_value = f"{x_token}[{x_idx}][i]"            
            x_token = self.clean_token(ret_buff.get_token()) + "_shadow"
            x_value = f"{x_token}[{x_idx}]"
            shadow_update = f"\n\t{x_value} = {ret_var_code};"

        return f"{ret_var_code} = {cast_operator} {function_name}({arg_vars_code});{shadow_update}"
    
    # def is_pointer_function(self, type) -> bool:
    #     return isinstance(type, PointerType) and type.get_base_type().to_function
    #     arg_types[p].to_function
    
    def full_type_emit(self, type, with_const: bool = True):
        
        if isinstance(type, PointerType):
            
            base_token = self.clean_token(type.get_base_type().get_token())
            consts = type.get_all_consts()
            if not with_const:
                consts = [False for _ in consts]
                
            pointer_level = DataLayout.get_ptr_level(type)
            
            s = ""
            
            i = 0
            while i < pointer_level:
                if consts[i]:
                    s += "const "
                if i == 0:
                    s += f"{base_token} "
                s += "* "
                i = i + 1
            
            # print(f"full_type_emit {type}")
            # from IPython import embed; embed(); exit(1)
            
            return s
            
        else:
            return self.type_emit(type)
    
    def has_some_const(self, type):
        if isinstance(type, PointerType):
            return any(type.get_all_consts())
        
        return type.is_const
    
    # Value
    def value_emit(self, value: Value, depth: int = -1) -> str:
        if isinstance(value, Variable):
            return self.variable_emit(value, depth)
        if isinstance(value, Address):
            return self.address_emit(value, depth)
        if isinstance(value, NullConstant):
            return self.nullconst_emit(value)
        if isinstance(value, Function):
            return self.function_emit(value)
        if isinstance(value, Constant):
            return self.constant_emit(value)

        raise Exception(f"I don't know {value}")
    
    # Constant
    def constant_emit(self, const: Constant):
        return f"{const.value}"

    # Function
    def function_emit(self, function: Function):
        return f"&{function.token}"

    # NullConstant
    def nullconst_emit(self, nullcnst: NullConstant) -> str:
        return "NULL"

    def clean_token(self, token: str) -> str:
        t = token.replace("%", "").replace("*", "")
        if "." in t:
            t = t.split(".")[-1]
        return t

    # Variable
    def variable_emit(self, variable: Variable, depth=-1) -> str:
        idx     = variable.get_index()
        buffer  = variable.get_buffer()
        token   = self.clean_token(buffer.token)
        type    = buffer.get_type()
        
        if depth != -1:
            extr_lvl = "[0]" * depth
            return f"{token}[{idx}]{extr_lvl}"    

        return f"{token}[{idx}]"

    # Type
    def type_emit(self, type: Type) -> str:
        if isinstance(type, PointerType):
            type = type.get_pointee_type()
        
        return self.clean_token(type.token)
