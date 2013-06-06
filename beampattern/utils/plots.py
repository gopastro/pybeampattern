#!/usr/bin/python

from beampattern.utils.configuration import Configuration
from beampattern.utils.beampattern_exceptions import BeamPatternGeneralError, BeamPatternArgumentError
import matplotlib.pyplot as plt
import re
import os

class BeamPlot(object):
    def __init__(self, filename):
        self.filename = filename
        self.cfgfile = self._get_cfg_file()
        self.cfg = self._get_configuration()
        
    def _get_cfg_file(self):
        fp = open(self.filename, 'r')
        jnk = fp.readline()
        second = fp.readline().strip()
        match = re.match('# Configfile: (?P<cfgfile>\w+\.\w+)', second)
        if match:
            fp.close()
            return match.groupdict()['cfgfile']
        else:
            fp.close()
            raise BeamPatternGeneralError('get_cfg_file', "Could not parse config file from input file")

    def _get_configuration(self):
        if self.cfgfile and os.path.exists(self.cfgfile):
            config = Configuration(self.cfgfile)
            return config.cfg
        else:
            raise BeamPatternGeneralError('get_configuration', "Could not parse configuration from config file")
