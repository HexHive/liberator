import sys, logging
logger = logging.getLogger("generator")
for func in ('debug', 'info', 'warning', 'error', 'critical'):
    setattr(sys.modules[__name__], func, getattr(logger, func))

from .Pool          import Pool
from .Configuration import Configuration
from .Generator     import Generator