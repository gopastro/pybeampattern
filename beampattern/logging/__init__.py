"""
Logging Framework for pybeammap
TODO: Simple test cases
"""

import logging as pylogging
import logging.handlers as handlers
import os
#from dreampy import dreampyParams

DEBUG0 = 5
DEBUG1 = 6
DEBUG2 = 7
DEBUG3 = 8
DEBUG4 = 9
DEBUG  = 10
INFO   = 20
WARNING = 30
ERROR  = 40
CRITICAL = 50

def _get_beammap_logname():
    """
    Returns the path to the beammap log file
    """
    if os.environ.has_key('HOME'):
        home = os.environ['HOME']
        if not os.path.exists(os.path.join(home, '.beammap')):
            os.mkdir(os.path.join(home, '.beammap'))
        fname = os.path.join(home, '.beammap', 'beammap.log')
        return fname
    else:
        return 'beammap.log'


class NullHandler(pylogging.Handler):
    """A simple NullHandler to be used by modules used
    inside beammap 
    Every module can use at least this one null handler.
    It does not do anything. The application that uses the
    beammap library can set up logging, and setup appropriate
    handlers, and then the beammap library will appropriately
    handle correct logging.
    A beammap module should do the following:
    from beammap.logging import logger
    logger.name = __name__  #to appropriately catch that module's logs
    And then you can use the logger object within the modules
    """
    def emit(self, record):
        pass

def will_debug():
    return logger.isEnabledFor(pylogging.DEBUG)

def add_file_handler(log, fname):
    handler = handlers.RotatingFileHandler(fname, maxBytes=20480,
                                           backupCount=5)
    # create formatter
    formatter = pylogging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    #level = beammapParams['beammap'].get('loglevel', 10)
    #handler.setLevel(level)
    handler.setLevel(pylogging.DEBUG)
    handler.setFormatter(formatter)
    #print "Setting up Rotating File Handler %s" % fname
    log.addHandler(handler)

def add_stream_handler(log):
    handler = pylogging.StreamHandler()
    #level = beammapParams['beammap'].get('loglevel', 10)
    handler.setLevel(pylogging.DEBUG)
    #handler.setLevel(level)
    log.addHandler(handler)

def debug_factory(logger, debug_level):
    def custom_debug(msg, *args, **kwargs):
        if logger.level >= debug_level:
           return
        logger._log(debug_level, msg, args, kwargs)
    return custom_debug    


logger = pylogging.getLogger('beammap')
logger.logging = pylogging
logger.addHandler(NullHandler())
logger.will_debug = will_debug
add_file_handler(logger, _get_beammap_logname())
add_stream_handler(logger)
logger.setLevel(DEBUG0)

for i in range(5, 10):
    pylogging.addLevelName(i, 'DEBUG%i' % (i-5))
    setattr(logger, 'debug%i' % (i-5), debug_factory(logger, i))
