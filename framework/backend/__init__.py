import sys, logging
logger = logging.getLogger("dependency")
for func in ('debug', 'info', 'warning', 'error', 'critical'):
    setattr(sys.modules[__name__], func, getattr(logger, func))

from .GrammarFeedback   import GrammarFeedback
from .BackendDriver     import BackendDriver

from .mock.MockBackendDriver    import MockBackendDriver
from .libfuzz.LFBackendDriver   import LFBackendDriver
