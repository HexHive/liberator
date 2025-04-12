import random, copy, re
from typing import List, Set, Dict, Tuple, Optional

from grammar import Grammar, Terminal, NonTerminal
from common import Api
from driver import Driver, Context
from driver.factory import Factory
from driver.ir import Statement, ApiCall, BuffDecl, Type, PointerType, Variable, Address

class OTFactory(Factory):
    concretization_logic: Dict[Terminal, ApiCall]
    dependency_graph    : Dict[Api, Set[Api]]

    def __init__(self, api_list: Set[Api], driver_size: int,
                    grammar: Grammar, max_nonterminals: int = 3):
        self.concretization_logic = self.load_concretization_logic(api_list)
        self.max_nonterminals = max_nonterminals
        self.driver_size = driver_size
        self.grammar = grammar
        self.dependency_graph = grammar.dependency_graph

    def create_random_driver(self) -> Driver:
        driver_context_free = self.generate_driver_context_free(self.grammar)
        driver_second = self.generate_driver_context_aware(driver_context_free)
        return driver_second

    def load_concretization_logic(self, apis_list: List[Api]) -> Dict[Terminal, ApiCall]:

        concretization_logic = {}

        for api in apis_list:
            stmt = Factory.api_to_apicall(api)
            for a in stmt.arg_types:
                if isinstance(a, PointerType):
                    bb = a.get_base_type()
            concretization_logic[Terminal(api.function_name)] = stmt
            
        return concretization_logic

    def nonterminals(self, terms):
        return [s for s in terms if isinstance(s, NonTerminal) ]

    def generate_driver_context_free(self, grammar: Grammar):

        symbols = [grammar.get_start_symbol()]
        expansion_trials = 0

        while len(self.nonterminals(symbols)) > 0 and len(symbols) <= self.driver_size:
            symbol_to_expand = random.choice(self.nonterminals(symbols))

            expansions = grammar[symbol_to_expand]
            expansion = random.choice(tuple(expansions))

            old_symbol_idx = symbols.index(symbol_to_expand)
            del symbols[old_symbol_idx]
            for i, e in enumerate(expansion):
                symbols.insert(old_symbol_idx + i, e)

            if len(self.nonterminals(symbols)) < self.max_nonterminals:
                expansion_trials = 0
            else:
                expansion_trials += 1
                if expansion_trials >= self.max_expansion_trials:
                    raise Exception(f"Cannot expand {symbol_to_expand}")

        symbols_only_terminal = []
        for s in symbols:
            if s.name == "start":
                continue

            if isinstance(s, Terminal):
                symbols_only_terminal += [copy.deepcopy(s)]
            elif isinstance(s, NonTerminal):
                symbols_only_terminal += [copy.deepcopy(s).convertToTerminal()]
            else:
                raise Exception(f"what is '{s}'?")

        return symbols_only_terminal

    def generate_driver_context_aware(self, driver_ctx_free) -> Driver:

        new_statement = lambda x: copy.deepcopy(self.concretization_logic[x]) 
        statements = [ new_statement(s) for s in driver_ctx_free if s.name != "end" ]
        
        # from IPython import embed; embed(); exit()
        
        context = Context()
        for statement in statements:
            if isinstance(statement, ApiCall):
                for arg_pos, arg_type in statement.get_pos_args_types():
                    if context.is_void_pointer(arg_type):
                        arg_var = context.randomly_gimme_a_var(context.stub_char_array, statement.function_name)
                    elif isinstance(arg_type, PointerType) and arg_type.to_function:
                        arg_var = context.get_function_pointer(arg_type)
                    else:
                        arg_var = context.randomly_gimme_a_var(arg_type, statement.function_name)
                    statement.set_pos_arg_var(arg_pos, arg_var)

                if statement.is_vararg:

                    for i, _ in enumerate(statement.vararg_var):
                        # type.get_pointee_type() == self.stub_void):
                        new_buff = context.create_new_var(context.stub_char_array, False)
                        val = new_buff.get_address()
                        var_t = None
                        if isinstance(val, Address):
                            var_t = val.get_variable()
                        elif isinstance(val, Variable):
                            var_t = val
                        statement.vararg_var[i] = var_t.get_address()

                # if isinstance(statement.ret_type, PointerType):
                #     from IPython import embed; embed(); exit()
                #     ret_var = self.context.randomly_gimme_a_var(self.context.stub_void, statement.function_name, True)
                # else:
                if context.is_void_pointer(statement.ret_type):
                    ret_var = context.randomly_gimme_a_var(copy.deepcopy(context.stub_char_array), statement.function_name, True)
                elif isinstance(statement.ret_type, PointerType) and statement.ret_type.to_function:
                    ret_var = context.get_null_constant()
                else:
                    ret_var = context.randomly_gimme_a_var(statement.ret_type, statement.function_name, True)
                statement.set_ret_var(ret_var)
            else:
                raise Exception(f"Don't know {statement}")

        statements_buffdecl = context.generate_buffer_decl()
        statements_buffinit = context.generate_buffer_init()

        stub_functions = context.get_stub_functions()

        d = Driver(statements_buffdecl + statements_buffinit + statements, context)
        d.add_stub_functions(stub_functions)

        return d