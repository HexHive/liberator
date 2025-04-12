import sys, logging
logger = logging.getLogger("constraint_based_search")
for func in ('debug', 'info', 'warning', 'error', 'critical'):
    setattr(sys.modules[__name__], func, getattr(logger, func))

from .CBSFactory               import CBSFactory