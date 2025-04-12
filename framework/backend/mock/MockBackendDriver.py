from driver import Driver
from driver.ir import ApiCall, BuffDecl, BuffInit, Type, PointerType, Address, Variable, Statement, Value, NullConstant
from backend import BackendDriver

import random, string, os

class MockBackendDriver(BackendDriver):

    def __init__(self, working_dir, seeds_dir, num_seeds):
        self.working_dir = working_dir
        self.seeds_dir = seeds_dir
        self.num_seeds = num_seeds
        self._idx = 0

    def get_name(self) -> str:
        file_name = f"Driver{self._idx}.txt"
        self._idx = self._idx + 1

        return file_name

    def emit_seeds(self, driver, driver_filename: str):
        #NOTE: the mock backend does not generate any seed
        return 

    # this return the filename
    def emit_driver(self, driver: Driver, driver_filename: str):

        # file name for the driver
        # driver_filename = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)) + ".txt"

        # driver_filename = "CEOBJLE6DR.txt"

        stmt_instances = []

        for stmt in driver:
            stmt_instances.append(self.stmt_emit(stmt))

        with open(os.path.join(self.working_dir, driver_filename), "w") as f:
            for stmt in stmt_instances:
                f.write(stmt + "\n")

        # print(driver.get_input_size())

        # return driver_filename

    # Address
    def address_emit(self, address: Address) -> str:
        variable = address.variable
        return f"&{self.variable_emit(variable)}"

    def stmt_emit(self, stmt: Statement) -> str:
        if isinstance(stmt, BuffDecl):
            return self.buffdec_emit(stmt)
        elif isinstance(stmt, ApiCall):
            return self.apicall_emit(stmt)
        elif isinstance(stmt, BuffInit):
            return ""
        raise NotImplementedError

    # BuffDecl
    def buffdec_emit(self, buffdecl: BuffDecl) -> str:
        buffer      = buffdecl.get_buffer()

        type        = buffer.get_type()
        n_element   = buffer.get_number_elements()
        token       = self.clean_token(buffer.get_token())

        return f"{self.type_emit(type)} {token}[{n_element}] = input();"

    # ApiCall
    def apicall_emit(self, apicall: ApiCall) -> str:
        ret_var = apicall.ret_var
        ret_type = apicall.ret_type
        arg_vars = apicall.arg_vars
        function_name = apicall.function_name

        ret_var_code = self.value_emit(ret_var)
        arg_vars_code = ", ".join([self.value_emit(a) for a in arg_vars])

        if ret_type == Type("void"):
            return f"{function_name}({arg_vars_code});"

        return f"{ret_var_code} = {function_name}({arg_vars_code});"
    
    # Value
    def value_emit(self, value: Value) -> str:
        if isinstance(value, Variable):
            return self.variable_emit(value)
        if isinstance(value, Address):
            return self.address_emit(value)
        if isinstance(value, NullConstant):
            return self.nullconst_emit(value)

        raise Exception(f"I don't know {value}")

    # NullConstant
    def nullconst_emit(self, nullcnst: NullConstant) -> str:
        return "NULL"

    def clean_token(self, token: str) -> str:
        t = token.replace("%", "").replace("*", "")
        if "." in t:
            t = t.split(".")[-1]
        return t

    # Variable
    def variable_emit(self, variable: Variable) -> str:
        idx     = variable.get_index()
        buffer  = variable.get_buffer()
        token   = self.clean_token(buffer.token)

        return f"{token}[{idx}]"

    # Type
    def type_emit(self, type: Type) -> str:
        if isinstance(type, PointerType):
            type = type.get_pointee_type()
        
        return self.clean_token(type.token)