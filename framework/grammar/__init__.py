import sys, logging
logger = logging.getLogger("dependency")
for func in ('debug', 'info', 'warning', 'error', 'critical'):
    setattr(sys.modules[__name__], func, getattr(logger, func))

from .Symbol            import Symbol
from .Grammar           import Grammar
from .Terminal          import Terminal
from .NonTerminal       import NonTerminal
from .ExpantionRule     import ExpantionRule
from .GrammarGenerator  import GrammarGenerator

# for grammar specialization
# from .type.TypeDependencyGraphGenerator import TypeDependencyGraphGenerator