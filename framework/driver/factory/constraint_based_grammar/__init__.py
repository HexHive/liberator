import sys, logging
logger = logging.getLogger("constraint_based_grammar")
for func in ('debug', 'info', 'warning', 'error', 'critical'):
    setattr(sys.modules[__name__], func, getattr(logger, func))

from .CBGFactory               import CBGFactory
from .CBGFactory               import ApiSeqState