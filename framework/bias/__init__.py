import sys, logging
logger = logging.getLogger("bias")
for func in ('debug', 'info', 'warning', 'error', 'critical'):
    setattr(sys.modules[__name__], func, getattr(logger, func))

from .Bias              import Bias
from .WBias             import WBias
from .SBias             import SBias
from .IBias             import IBias
from .FBias             import FBias