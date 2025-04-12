#!/usr/bin/env python3

import re, random

RE_NONTERMINAL = re.compile(r'(<[^<> ]*>)')

def nonterminals(expansion):
    # In later chapters, we allow expansions to be tuples,
    # with the expansion being the first element
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
                raise ExpansionError("Cannot expand " + repr(term))

    return term

def main():
    grammar = {"<start>":
            ["<expr>"],

        "<expr>":
            ["<term> + <expr>", "<term> - <expr>", "<term>"],

        "<term>":
            ["<factor> * <term>", "<factor> / <term>", "<factor>"],

        "<factor>":
            ["+<factor>",
            "-<factor>",
            "(<expr>)",
            "<integer>.<integer>",
            "<integer>"],

        "<integer>":
            ["<digit><integer>", "<digit>"],

        "<digit>":
            ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    }

    for i in range(10):
        print(simple_grammar_fuzzer(grammar=grammar, start_symbol="<start>", max_nonterminals=3, log=False))

    print("[+] DONE")

if __name__ == "__main__":
    main()