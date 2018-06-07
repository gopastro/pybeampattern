"""
Read a default configuration file for default values
and save it upon each exit. Next time we fire up, use those
default values.

This uses python's configobj library.
"""

from configobj import ConfigObj,flatten_errors
from validate import Validator
from beampattern.logging import logger

import os
import types

logger.name = __name__

config_spec_text = """
#beampattern general items
[general]
#loglevel can be one of these. If loglevel is set to 20 (say)
#then only messages with a loglevel higher than 20 will be emitted
#default loglevel is 10
# List of loglevels:
# Name    Level
# DEBUG0 : 5
# DEBUG1 : 6
# DEBUG2 : 7
# DEBUG3 : 8
# DEBUG4 : 9
# DEBUG  : 10
# INFO   : 20
# WARNING: 30
# ERROR  : 40
# CRITICAL: 50
# fileloglevel is for dreampy.log in .dreampyrc
# consoleloglevel is for console printout
fileloglevel  = integer(5, 50, default=10)
consoleloglevel  = integer(5, 50, default=10)
# comment is a long string which gets written to the output data file
comment = string(max=150, default="BeamMap at 74 GHz")

#general plot specific items
[plot]
#figsize is figure size in pixels (x,y)
figsize = int_list(min=2, max=2, default=list(800, 600))
#more plot configs to follow later

[devices]
# use the unidex11?
use_unidex = boolean(default=True)
# use vector network analyzer?
use_vv = boolean(default=True)

[azimuth]
#This object contains configuration items specific to maps
#in azimuth
# xmin: map start position in degrees
xmin = float(-180.0, 180.0, default=-90)
# xmax: map end position in degrees
xmax = float(-180.0, 180.0, default=90)
# xinc: map step in degrees
xinc = float(0.1, 180.0, default=1.0)
# xmap_vel: map velocity in degrees/second
xmap_vel = float(0.1, 30.0, default=2.0)
# xslew_vel: slew velocity in degrees/second
xslew_vel = float(0.1, 30.0, default=5.0)

[elevation]
#This object contains configuration items specific to maps
#in elevation
# ymin: map start position in degrees
ymin = float(-180.0, 180.0, default=-90)
# ymax: map end position in degrees
ymax = float(-180.0, 180.0, default=90)
# yinc: map step in degrees
yinc = float(0.1, 180.0, default=1.0)

[synthesizer]
# This object contains configuration items specific to 
# setting frequencies in synth
freq = float_list(min=1, max=100, default=list(11.7, 12.0, 12.2))

[vector_voltmeter]
# This object contains configuration items specfic to
# frequency and frequency sweeps
# freq is a list of floats
meas = string(max=10, default="TRAN")
avg_value = integer(1, 4096, default=3)
"""

def default_config():
    cfg_spec = ConfigObj(config_spec_text.splitlines(), list_values=False)
    valid = Validator()
    cfg = ConfigObj(configspec=cfg_spec, stringify=True, list_values=True)
    test = cfg.validate(valid, copy=True)
    if test:
        return cfg

def validate_dictionary(cdic):
    """This function validates a dictionary against the config spec here"""
    cfg_spec = ConfigObj(config_spec_text.splitlines(), list_values=False)
    valid = Validator()
    cfg = ConfigObj(cdic, configspec=cfg_spec)
    rtn = cfg.validate(valid, preserve_errors=True)
    if type(rtn) == types.BooleanType and rtn:
        return True
    else:
        res = flatten_errors(cfg, rtn)
        errortxt = ''
        for row in res:
            errortxt += 'In Section %s, key %s has error: %s' % (row[0], row[1], row[2])
            logger.error(errortxt)
        return False
    
class ConfigurationVector:
    def __init__(self, filename):
        """Initializes a config file if does not exist. If exists, uses
        it to validate the file, and setup default initial parameters"""
        self.cfg_spec = ConfigObj(config_spec_text.splitlines(), list_values=False)
        self.cfg_filename = filename
        valid = Validator()
        if not os.path.exists(self.cfg_filename):
            #no configuration file found
            logger.info("File %s not found, so creating one from you from defaults" % self.cfg_filename)
            cfg = ConfigObj(configspec=self.cfg_spec, stringify=True, list_values=True)
            cfg.filename = self.cfg_filename
            test = cfg.validate(valid, copy=True)
            cfg.write()
        self.cfg = ConfigObj(self.cfg_filename, configspec=self.cfg_spec)
        rtn = self.cfg.validate(valid, preserve_errors=True)
        if type(rtn) == types.BooleanType and rtn:
            logger.info("Config file validated")
            self.tested = True
        else:
            self.tested = False
            res = flatten_errors(self.cfg, rtn)
            self.errortxt = ''
            for row in res:
                self.errortxt += 'In Section %s, key %s has error: %s' % (row[0], row[1], row[2])
            logger.error(self.errortxt)

    def save_config(self, new_config, filename=None):
        """Writes the config file upon exiting the program"""
        self.cfg.update(new_config)
        if filename is None:
            self.cfg.filename = self.cfg_filename
        else:
            self.cfg.filename = filename
        self.cfg.write()
        logger.info("Config file %s written out" % self.cfg.filename)
