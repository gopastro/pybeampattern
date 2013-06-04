#!/usr/bin/python

from optparse import OptionParser
import sys, os
import numpy
import time
import datetime
import pylab

from beampattern.utils.configuration import Configuration
from beampattern.logging import logger

logger.name = __name__
        
if __name__ == '__main__':
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-c", "--config",
                      action="store", type="string",
                      dest="configfile", default="beammap.cfg",
                      help="Input Configuration file for beammap")
    parser.add_option("-f", "--filename",
                      action="store", type="string",
                      dest="filename", default="beamscan.txt",
                      help="Ascii Filename to store data into")

    (options, args) = parser.parse_args()

    if options.configfile:
        if os.path.exists(options.configfile):
            logger.info("Using configuration file %s" % options.configfile)
        else:
            logger.info("Will create configuration file %s from defaults" % options.configfile)
        cfg = Configuration(options.configfile)
    if options.filename:
        base, ext = os.path.splitext(options.filename)        
        datetime_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = base+"_"+datetime_str+ext
        logger.info("Will write output to %s" % filename)

    sys.exit(0)

