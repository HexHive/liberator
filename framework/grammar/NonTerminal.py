from . import Symbol, Terminal

class NonTerminal(Symbol):
    def convertToTerminal(self):
        return Terminal.Terminal(self.name)