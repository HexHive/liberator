import sys, logging
logger = logging.getLogger("factory")
for func in ('debug', 'info', 'warning', 'error', 'critical'):
    setattr(sys.modules[__name__], func, getattr(logger, func))

from .Factory               import Factory
from .Factory               import EmptyDriverSpace

import driver.factory.only_type
import driver.factory.constraint_based
import driver.factory.constraint_based_search
import driver.factory.constraint_based_grammar
import driver.factory.constraint_based_backward