import sys, logging
logger = logging.getLogger("constraint_based")
for func in ('debug', 'info', 'warning', 'error', 'critical'):
    setattr(sys.modules[__name__], func, getattr(logger, func))

from .CBFactory               import CBFactory