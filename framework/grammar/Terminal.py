from . import Symbol, NonTerminal

class Terminal(Symbol):
    def convertToNonTerminal(self):
        return NonTerminal(self.name)    
