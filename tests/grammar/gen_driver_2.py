#!/usr/bin/env python3

import re, random

RE_NONTERMINAL = re.compile(r'(<[^<> ]*>)')

def nonterminals(expansion):
    if isinstance(expansion, tuple):
        expansion = expansion[0]

    return RE_NONTERMINAL.findall(expansion)

def simple_grammar_fuzzer(grammar, start_symbol, max_nonterminals, max_expansion_trials = 100,  log = False):
    """Produce a string from `grammar`.
       `start_symbol`: use a start symbol other than `<start>` (default).
       `max_nonterminals`: the maximum number of nonterminals 
         still left for expansion
       `max_expansion_trials`: maximum # of attempts to produce a string
       `log`: print expansion progress if True"""

    term = start_symbol
    expansion_trials = 0

    while len(nonterminals(term)) > 0:
        symbol_to_expand = random.choice(nonterminals(term))
        expansions = grammar[symbol_to_expand]
        expansion = random.choice(expansions)
        # In later chapters, we allow expansions to be tuples,
        # with the expansion being the first element
        if isinstance(expansion, tuple):
            expansion = expansion[0]

        new_term = term.replace(symbol_to_expand, expansion, 1)

        if len(nonterminals(new_term)) < max_nonterminals:
            term = new_term
            if log:
                print("%-40s" % (symbol_to_expand + " -> " + expansion), term)
            expansion_trials = 0
        else:
            expansion_trials += 1
            if expansion_trials >= max_expansion_trials:
                raise Exception("Cannot expand " + repr(term))

    return term

# statements_semantic = {}

# class SemanticObject:
#     def __init__(self):
#         pass

def create_new_var(t, context, context_counter):
    var_counter = context_counter.get(t, 0)
    new_var = f"{t}_{var_counter}".replace("$", "")
    context[new_var] = t
    context_counter[t] = var_counter + 1

    return new_var

def get_random_var(thet, context):
    a_var = random.choice([v for v, t in context.items() if t == thet])  

    return a_var

def has_vars_type(a_t, context):
    for v, t in context.items():
        if t == a_t:
            return True

    return False

def generate_init_vars(context):

    statements = []

    for v, t in context.items():
        statements += [f"{t[1:]} {v} = input();"]
        # statements += [f"{t[1:]} {v[1:]} = input();"]

    return statements

def get_address_of(variable):
    return f"&{variable}"

def expand_rules(sequence):

    statements = []

    for token in sequence.split(";"):
        if token == "open_conn":
            statements += ["open_conn($*char, $int, $*conn);"]
        elif token == "send":
            statements += ["$int = send($*char, $int, $conn);"]
        elif token == "recv":
            statements += ["int = send($*char, $int, $conn);"]
        elif token == "close_conn":
            statements += ["close_conn($*conn);"]

        # if token == "open_conn":
        #     statements += ["open_conn($ip, $port, $*conn);"]
        # elif token == "send":
        #     statements += ["$send_ret = send($*buff, $buff_len, $conn);"]
        # elif token == "recv":
        #     statements += ["recv_ret = send($*buff, $buff_len, $conn);"]
        # elif token == "close_conn":
        #     statements += ["close_conn($*conn);"]

    GET_VARIABLES = re.compile(r'(\$[*a-z_]*)')

    statements_expanded = []

    context = {}
    context_counter = {}
    for statement in statements:
        variables = GET_VARIABLES.findall(statement)

        for t in variables:
            if t.startswith("$*"):

                tt = t.replace("$*", "$")
                
                # I can decide to add a new var to the context, if I want
                if random.getrandbits(1) == 1 or not has_vars_type(tt, context):
                    # print(f"=> I create a new {tt} to get the address")
                    v = create_new_var(tt, context, context_counter)
                # I pick a var from the context
                else:
                    # print(f"=> I get a random {tt} to get the address")
                    v = get_random_var(tt, context)

                v = get_address_of(v)
                statement = statement.replace(t, v)
                    
            else:
                # if v not in context -> just create
                if not has_vars_type(t, context):
                    # print(f"=> {t} not in context, new one")
                    v = create_new_var(t, context, context_counter)
                    statement = statement.replace(t, v)
                else:
                    # I might get an existing one
                    if random.getrandbits(1) == 1:
                        # print(f"=> wanna pick a random {t} from context")
                        v = get_random_var(t, context)
                        statement = statement.replace(t, v)
                    # or create a new var
                    else:
                        # print(f"=> decided to create a new {t}")
                        v = create_new_var(t, context, context_counter)
                        statement = statement.replace(t, v)
        

        statements_expanded += [statement]

    statements_context = generate_init_vars(context)

    return "\n".join(statements_context + [""] + statements_expanded)
        

def main():
    grammar = {"<start>": ["<open_conn>", "<close_conn>", "<send>", "<recv>", "<end>"],
        "<open_conn>": ["open_conn;<open_conn>", "open_conn;<send>", "open_conn;<close_conn>", "open_conn;<end>"],
        "<send>": ["send;<open_conn>", "send;<send>", "send;<close_conn>", "send;<recv>", "send;<end>"],
        "<recv>": ["recv;<open_conn>", "recv;<send>", "recv;<close_conn>", "recv;<recv>", "recv;<end>"],
        "<close_conn>": ["close_conn;<open_conn>", "close_conn;<send>", "close_conn;<close_conn>", "close_conn;<end>"],
        "<end>": [""] 
    }

    # for i in range(10):
    driver_first = simple_grammar_fuzzer(grammar=grammar, start_symbol="<start>", max_nonterminals=3, log=False)
    # print(driver_first)
    # print()
    driver_second = expand_rules(driver_first)
    print(driver_second)

if __name__ == "__main__":
    main()