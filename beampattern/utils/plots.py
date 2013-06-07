#!/usr/bin/python

from beampattern.utils.configuration import Configuration
from beampattern.utils.beampattern_exceptions import BeamPatternGeneralError, BeamPatternArgumentError
import matplotlib.pyplot as plt
import re
import os
import numpy

class BeamPlot(object):
    def __init__(self, filename, markers=True,
                 grid=True, plotfile=None):
        self.plot_symbols = ['o', 's', 'v', '^', '<', '>',
                             '1', '2', '3', '4', 'p', '*',
                             'h', 'H', '+', 'x', 'D', 'd']
        self.linestyles = ['-', '--', '-.', ':']
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
        match = re.match('# Comment: (?P<comment>[\w\s]*)', three)
        if match:
            self.comment = match.groupdict()['comment']

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
        return header
    
    def _plot_data(self, frequencies=None, linear=True):
        plt.ion()
        if frequencies is None:
            frequencies = self.cfg['synth']['freq']
            
        if not linear:
            vmax = -10000.
            for i, freq in enumerate(frequencies):
                if freq in self.cfg['synth']['freq']:
                    find = self.cfg['synth']['freq'].index(freq)*2 + 1
                    cmax = self.data[:, find].max()
                    vmax = cmax if cmax > vmax else vmax
        for i, freq in enumerate(frequencies):
            if freq in self.cfg['synth']['freq']:
                find = self.cfg['synth']['freq'].index(freq)*2 + 1
                lind = i % len(self.linestyles)
                pind = i % len(self.plot_symbols)
                if linear:
                    ydata = self.data[:, find]
                else:
                    ydata = 10.0 * numpy.log10(self.data[:, find]/vmax)
                if self.markers:
                    plt.plot(self.data[:, 0], ydata,
                             linestyle=self.linestyles[lind],
                             marker=self.plot_symbols[pind],
                             markersize=3,
                             label='%.1f GHz' % freq)
                else:
                    plt.plot(self.data[:, 0], ydata,
                             linestyle=self.linestyles[lind],
                             label='%.1f GHz' % freq)
        plt.xlim(self.cfg['azimuth']['xmin'], self.cfg['azimuth']['xmax'])
        plt.xlabel('Azimuth (deg)')
        plt.ylabel('Beam Voltage (linear)')
        plt.legend(loc='best')
        plt.title('%s; %s' % (self.comment, self.datetime_str))
        if self.grid:
            plt.grid(True)
        plt.draw()
        plt.show()
        if self.plotfile is not None:
            plt.savefig(self.plotfile)

    def plot_linear(self, frequencies=None):
        self._plot_data(frequencies=frequencies,
                        linear=True)
        

    def plot_log(self, frequencies=None):
        self._plot_data(frequencies=frequencies,
                        linear=False)



        
