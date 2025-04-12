import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__)))

# from common import ColoredLogger
# from functools import partial
# import logging
# logging.getLogger().handlers.clear()
# logging.setLoggerClass(ColoredLogger)
# root_logger = ColoredLogger()

import dependency, common, grammar, driver, backend, generator, constraints, bias

# import atexit
# from profiler import ProfilingStoppedEvent
# def exit_handler():
#     ProfilingStoppedEvent.set()
# atexit.register(exit_handler)