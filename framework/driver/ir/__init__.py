import sys, logging
logger = logging.getLogger("ir")
for func in ('debug', 'info', 'warning', 'error', 'critical'):
    setattr(sys.modules[__name__], func, getattr(logger, func))

from .Statement             import Statement
from .Type                  import Type
from .Type                  import TypeTag
from .PointerType           import PointerType
from .Value                 import Value
from .Variable              import Variable
from .Function              import Function
from .Address               import Address
from .NullConstant          import NullConstant
from .Constant              import Constant
from .ApiCall               import ApiCall
from .BuffDecl              import BuffDecl
from .ConstStringDecl       import ConstStringDecl
from .SetStringNull         import SetStringNull
from .BuffInit              import BuffInit
from .FileInit              import FileInit
from .DynArrayInit          import DynArrayInit
from .DynDblArrInit         import DynDblArrInit
from .Buffer                import Buffer
from .Buffer                import AllocType
from .AssertNull            import AssertNull
from .CleanBuffer           import CleanBuffer
from .CleanDblBuffer        import CleanDblBuffer
from .SetNull               import SetNull