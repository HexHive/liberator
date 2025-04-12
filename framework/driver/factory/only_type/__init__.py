import sys, logging
logger = logging.getLogger("only_type")
for func in ('debug', 'info', 'warning', 'error', 'critical'):
    setattr(sys.modules[__name__], func, getattr(logger, func))

from .OTFactory               import OTFactory