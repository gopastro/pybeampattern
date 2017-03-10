#!/usr/bin/python

from beampattern.utils.configuration import Configuration
from beampattern.utils.phase_configuration import ConfigurationPhase
from beampattern.utils.beampattern_exceptions import BeamPatternGeneralError, BeamPatternArgumentError
import matplotlib.pyplot as plt
import re
import os
import numpy
import pandas as pd

class BeamIntegral(object):
    def __init__(self, filename, markers=True,
                 grid=True, plotfile=None):
        self.filename = filename
        self._get_cfg_file()
        self.cfg = self._get_configuration()
        self.data = self._get_data()
        self.header = self._get_header()
        self.markers = markers
        self.grid = grid
        self.plotfile = plotfile
        
    def _get_cfg_file(self):
        fp = open(self.filename, 'r')
        first = fp.readline()
        match = re.match('# Beammap Timestamp: (?P<datetime_str>\w+)', first)
        if match:
            self.datetime_str = match.groupdict()['datetime_str']
        second = fp.readline().strip()
        match = re.match('# Configfile: (?P<cfgfile>\w+\.\w+)', second)
        if match:
            self.cfgfile = match.groupdict()['cfgfile']
        else:
            raise BeamPatternGeneralError('get_cfg_file', "Could not parse config file from input file")
        three = fp.readline().strip()
        #match = re.match('# Comment: (?P<comment>[\w\s]*)', three)
        #if match:
        #    self.comment = match.groupdict()['comment']

    def _get_configuration(self):
        if self.cfgfile and os.path.exists(self.cfgfile):
            config = Configuration(self.cfgfile)
            return config.cfg
        else:
            raise BeamPatternGeneralError('get_configuration', "Could not parse configuration from config file")

    def _get_data(self):
        return numpy.loadtxt(self.filename, delimiter=',')

    def _get_header(self):
        fp = open(self.filename, 'r')
        header = ''
        for line in fp.readlines():
            if line[0] == '#':
                header += line
            else:
                break
        fp.close()
        try:
            offstr = re.findall('Voltage offset: (?P<offset>\d+\.\d+)', header)[0]
            self.offset = float(offstr)
        except:
            self.offset = 0.0
        return header
    
    def integrate(self, frequencies=None, 
                  radius=2.7, nooffset=False,
                  azel='az'):
        """
        Given a radius calculate beam integral inside the radius and
        also the total integral
        """
        if frequencies is None:
            frequencies = self.cfg['synth']['freq']
        lisdic = []
        for i, freq in enumerate(frequencies):
            if freq in self.cfg['synth']['freq']:
                dic = {}
                dic['frequency'] = freq
                if azel in ('az', 'el'):
                    find = self.cfg['synth']['freq'].index(freq)*2 + 1
                else:
                    find = self.cfg['synth']['freq'].index(freq)*2 + 2
                if not nooffset:
                    ydata = numpy.sqrt(self.data[:, find]**2 - self.offset**2)
                else:
                    ydata = self.data[:, find]
                if azel in ('az', 'el'):
                    xdata = self.data[:, 0]
                else:
                    xdata = numpy.sqrt(self.data[:, 0]**2 + self.data[:, 1]**2)
                    ind = numpy.where(self.data[:, 0] < 0)
                    xdata[ind] = -xdata[ind]
                idx = numpy.where(numpy.abs(xdata) <= radius)
                dic['inner'] = numpy.nansum(ydata[idx])
                dic['all'] = numpy.nansum(ydata)
                lisdic.append(dic)
                print freq, dic['inner'], dic['all']
        return pd.DataFrame(lisdic)
    
