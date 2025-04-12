import sys, logging
logger = logging.getLogger("dependency")
for func in ('debug', 'info', 'warning', 'error', 'critical'):
    setattr(sys.modules[__name__], func, getattr(logger, func))

from .utils         import Utils, CoerceFunction, CoerceArgument
from .datalayout    import DataLayout
from .api           import Api, Arg
from .conditions    import FunctionConditionsSet, FunctionConditions
from .conditions    import AccessTypeSet, AccessType, Access, ValueMetadata