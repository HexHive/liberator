
from dependency import DependencyGraph

from . import Grammar, Terminal, NonTerminal, Symbol, ExpantionRule
from driver.factory import Factory

class GrammarGenerator:
    def __init__(self, start_term, end_term):
        self.start_term = start_term
        self.end_term = end_term

    def create(self, dgraph: DependencyGraph) -> Grammar:

        grammar = Grammar(self.start_term)

        inv_dep_graph = dict((k, set()) for k in list(dgraph.keys()))

        # print(dep_graph)

        for api, deps in dgraph.items():
            for dep in deps:
                if not dep in inv_dep_graph:
                    inv_dep_graph[dep] = set()
                
                inv_dep_graph[dep].add(api)

        for api in inv_dep_graph.keys():
            if not self.has_incomplete_type(api):
                nt = NonTerminal(api.function_name)
                expantion_rule = ExpantionRule([nt])
                grammar.add_expantion_rule(self.start_term, expantion_rule)

        expantion_rule = ExpantionRule([self.end_term])
        grammar.add_expantion_rule(self.start_term, expantion_rule)


        for api, nexts in inv_dep_graph.items():
            # nt = NonTerminal(api.function_name + "_nt")
            nt = NonTerminal(api.function_name)
            t = Terminal(api.function_name)

            for n in nexts:
                # nnt = NonTerminal(n.function_name + "_nt")
                nnt = NonTerminal(n.function_name)
                expantion_rule = ExpantionRule([t, nnt])
                grammar.add_expantion_rule(nt, expantion_rule)

            expantion_rule = ExpantionRule([t, nt])
            grammar.add_expantion_rule(nt, expantion_rule)

            expantion_rule = ExpantionRule([t, self.start_term])
            grammar.add_expantion_rule(nt, expantion_rule)

        grammar.dependency_graph = inv_dep_graph

        return grammar

    def has_incomplete_type(self, api):

        arg_list_type = []
        for _, arg in enumerate(api.arguments_info):
            # NOTE: for simplicity, const type as arguments can be consider non-const, see `Driver_IR.md` for more info
            the_type = Factory.normalize_type(arg.type, arg.size, arg.flag, arg.is_const)
            arg_list_type += [the_type]

        return any(arg.is_incomplete for arg in arg_list_type)

#     # {"close": ["connect","close"],
#     # "connect": ["connect", "send_msg", "receive_msg", "close"],
#     # "receive_msg": [ "connect", "send_msg", "receive_msg", "close"],
#     # "send_msg": [ "connect", "send_msg", "receive_msg", "close" ] }

#     # {"<start>": ["<open_conn>", "<close_conn>", "<send>", "<recv>", "<end>"],
#     #     "<open_conn>": ["open_conn;<open_conn>", "open_conn;<send>", "open_conn;<close_conn>", "open_conn;<end>"],
#     #     "<send>": ["send;<open_conn>", "send;<send>", "send;<close_conn>", "send;<recv>", "send;<end>"],
#     #     "<recv>": ["recv;<open_conn>", "recv;<send>", "recv;<close_conn>", "recv;<recv>", "recv;<end>"],
#     #     "<close_conn>": ["close_conn;<open_conn>", "close_conn;<send>", "close_conn;<close_conn>", "close_conn;<end>"],
#     #     "<end>": [""] 
#     # }

#     