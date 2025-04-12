from abc import ABC, abstractmethod

from . import Symbol, NonTerminal, ExpantionRule

class Grammar(ABC):
    def __init__(self, start_symbol: NonTerminal):
        self.symbols = {}
        self.symbols[start_symbol] = set()
        self.start_symbol = start_symbol
    
    def add_expantion_rule(self, elem_nt: NonTerminal, exprule: ExpantionRule):
        if elem_nt not in self.symbols:
            self.symbols[elem_nt] = set()

        if exprule not in self.symbols[elem_nt]:
            self.symbols[elem_nt].add(exprule)

    def __getitem__(self, key):
        return self.symbols[key]

    def get_expansion_rules(self, elem: NonTerminal) -> [ExpantionRule]:
        if not elem in self.symbols:
            raise Exception(f"Element {elem} not in the grammar")

        return self.symbols[elem]

    def num_expansions(self):
        return len(self.expansion_list)

    def __iter__(self):
        for v in self.symbols:
            yield v

    def num_symbols(self):
        return len(self.symbols)

    def get_start_symbol(self):
        return self.start_symbol

    def __str__(self):
        return f"{self.__class__.__name__}(name={self.start_symbol.name}, n_elem={self.num_symbols()})"

    def pprint(self):
        print(self)
        # for e, elem in enumerate(self):
        for elem in self:
            print(f"{elem} \w {len(self.get_expansion_rules(elem))} rules:")
            for er in self.get_expansion_rules(elem):
                print(f"\t{er}")
    
