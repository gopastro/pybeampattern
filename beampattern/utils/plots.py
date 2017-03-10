#!/usr/bin/python

from beampattern.utils.configuration import Configuration
from beampattern.utils.phase_configuration import ConfigurationPhase
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
    
    def _plot_data(self, frequencies=None, linear=True,
                   ylim=None, xlim=None, title=None, 
                   azel='az', nooffset=False):
        print title
        plt.ion()
        if frequencies is None:
            frequencies = self.cfg['synth']['freq']
            
        # if not linear:
        #     vmax = -10000.
        #     for i, freq in enumerate(frequencies):
        #         if freq in self.cfg['synth']['freq']:
        #             find = self.cfg['synth']['freq'].index(freq)*2 + 1
        #             cmax = self.data[:, find].max()
        #             vmax = cmax if cmax > vmax else vmax
        for i, freq in enumerate(frequencies):
            if freq in self.cfg['synth']['freq']:
                if azel in ('az', 'el'):
                    find = self.cfg['synth']['freq'].index(freq)*2 + 1
                else:
                    find = self.cfg['synth']['freq'].index(freq)*2 + 2
                lind = i % len(self.linestyles)
                pind = i % len(self.plot_symbols)
                if linear:
                    if not nooffset:
                        ydata = numpy.sqrt(self.data[:, find]**2 - self.offset**2)
                    else:
                        ydata = self.data[:, find]
                else:
                    if not nooffset:
                        yd = numpy.sqrt(self.data[:, find]**2 - self.offset**2)
                    else:
                        yd = self.data[:, find]
                    arg = yd/numpy.nanmax(yd)
                    ind = numpy.where(arg <= 0.0)
                    ydata = 10.0 * numpy.log10(arg)
                    ydata[ind] = numpy.nan
                if self.markers:
                    if azel in ('az', 'el'):
                        plt.plot(self.data[:, 0], ydata,
                                 linestyle=self.linestyles[lind],
                                 marker=self.plot_symbols[pind],
                                 markersize=3,
                                 label='%.1f GHz' % freq)
                    else:
                        diag = numpy.sqrt(self.data[:, 0]**2 + self.data[:, 1]**2)
                        ind = numpy.where(self.data[:, 0] < 0)
                        diag[ind] = -diag[ind]
                        plt.plot(diag, ydata,
                                 linestyle=self.linestyles[lind],
                                 marker=self.plot_symbols[pind],
                                 markersize=3,
                                 label='%.1f GHz' % freq)                        
                else:
                    if azel in ('az', 'el'):
                        plt.plot(self.data[:, 0], ydata,
                                 linestyle=self.linestyles[lind],
                                 label='%.1f GHz' % freq)
                    else:
                        diag = numpy.sqrt(self.data[:, 0]**2 + self.data[:, 1]**2)
                        ind = numpy.where(self.data[:, 0] < 0)
                        diag[ind] = -diag[ind]
                        plt.plot(diag, ydata,
                                 linestyle=self.linestyles[lind],
                                 label='%.1f GHz' % freq)
                        
        if xlim is None:
            if azel == 'az':
                plt.xlim(self.cfg['azimuth']['xmin'], self.cfg['azimuth']['xmax'])
            elif azel == 'el':
                plt.xlim(self.cfg['elevation']['ymin'], self.cfg['elevation']['ymax'])
            elif azel == 'diag': 
                diag = numpy.sqrt(self.data[:, 0]**2 + self.data[:, 1]**2)
                ind = numpy.where(self.data[:, 0] < 0)
                diag[ind] = -diag[ind]               
                plt.xlim(diag[0], diag[-1])
        else:
            plt.xlim(xlim[0], xlim[1])
        if ylim is not None:
            plt.ylim(ylim[0], ylim[1])
        if azel == 'az':
            plt.xlabel('Azimuth (deg)')
        elif azel == 'el':
            plt.xlabel('Elevation (deg)')
        else:
            plt.xlabel('Diagonal (deg)')
        if linear:
            plt.ylabel('Beam Voltage (linear)')
        else:
            plt.ylabel('Beam Voltage (log)')
        plt.legend(loc='best')
        if title is None:
            plt.title('%s; %s' % (self.cfg['general']['comment'], self.datetime_str))
        else:
            plt.title(title)
        if self.grid:
            plt.grid(True)
        plt.draw()
        plt.show()
        if self.plotfile is not None:
            plt.savefig(self.plotfile)

    def plot_linear(self, frequencies=None, xlim=None,
                    ylim=None, title=None, azel='az', nooffset=False):
        self._plot_data(frequencies=frequencies,
                        linear=True, xlim=xlim, ylim=ylim,
                        title=title, azel=azel, nooffset=nooffset)
        

    def plot_log(self, frequencies=None, xlim=None,
                    ylim=None, title=None, azel='az', nooffset=False):
        self._plot_data(frequencies=frequencies,
                        linear=False, xlim=xlim, ylim=ylim,
                        title=title, azel=azel, nooffset=nooffset)


class BeamPlotPhase(object):
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

    def _get_configuration(self):
        if self.cfgfile and os.path.exists(self.cfgfile):
            config = ConfigurationPhase(self.cfgfile)
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
    
    def _plot_data_amp(self, frequencies=None, linear=True,
                       options=None):
        title = options.title
        print title
        plt.ion()
        plt.figure()
        if frequencies is None:
            frequencies = self.cfg['vna']['freq']
        for i, freq in enumerate(frequencies):
            if freq in self.cfg['vna']['freq']:
                find = self.cfg['vna']['freq'].index(freq)*2 + 1
                lind = i % len(self.linestyles)
                pind = i % len(self.plot_symbols)
                cdata = self.data[:, find] + 1j * self.data[:, find+1]
                if linear:
                    ydata = numpy.abs(cdata)
                else:
                    arg = numpy.abs(cdata)/numpy.abs(cdata).max()
                    ind = numpy.where(arg <= 0.0)
                    ydata = 10.0 * numpy.log10(arg)
                    ydata[ind] = numpy.nan
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
        if options.xlimamp is None:
            plt.xlim(self.cfg['azimuth']['xmin'], self.cfg['azimuth']['xmax'])
        else:
            plt.xlim(options.xlimamp[0], options.xlimamp[1])
        if options.ylimamp is not None:
            plt.ylim(options.ylimamp[0], options.ylimamp[1])
        plt.xlabel('Azimuth (deg)')
        if linear:
            plt.ylabel('Beam Voltage (linear)')
        else:
            plt.ylabel('Beam Voltage (log)')
        plt.legend(loc='best')
        if title is None:
            plt.title('%s; %s' % (self.cfg['general']['comment'], self.datetime_str))
        else:
            plt.title(title)
        if self.grid:
            plt.grid(True)
        plt.draw()
        plt.show()
        if self.plotfile is not None:
            ampfile = 'amp_' + self.plotfile
            plt.savefig(ampfile)

    def _plot_data_phase(self, frequencies=None, 
                         options=None):
        title = options.title
        print title
        plt.ion()
        plt.figure()
        if frequencies is None:
            frequencies = self.cfg['vna']['freq']
        for i, freq in enumerate(frequencies):
            if freq in self.cfg['vna']['freq']:
                find = self.cfg['vna']['freq'].index(freq)*2 + 1
                lind = i % len(self.linestyles)
                pind = i % len(self.plot_symbols)
                cdata = self.data[:, find] + 1j * self.data[:, find+1]
                if self.markers:
                    plt.plot(self.data[:, 0], numpy.degrees(numpy.angle(cdata)),
                             linestyle=self.linestyles[lind],
                             marker=self.plot_symbols[pind],
                             markersize=3,
                             label='%.1f GHz' % freq)
                else:
                    plt.plot(self.data[:, 0], numpy.degrees(numpy.angle(cdata)),
                             linestyle=self.linestyles[lind],
                             label='%.1f GHz' % freq)
        if options.xlimphase is None:
            plt.xlim(self.cfg['azimuth']['xmin'], self.cfg['azimuth']['xmax'])
        else:
            plt.xlim(options.xlimphase[0], options.xlimphase[1])
        if options.ylimphase is not None:
            plt.ylim(options.ylimphase[0], options.ylimphase[1])
        plt.xlabel('Azimuth (deg)')
        plt.ylabel('Beam Phase (deg)')
        plt.legend(loc='best')
        if title is None:
            plt.title('%s; %s' % (self.cfg['general']['comment'], self.datetime_str))
        else:
            plt.title(title)
        if self.grid:
            plt.grid(True)
        plt.draw()
        plt.show()
        if self.plotfile is not None:
            phasefile = 'phase_' + self.plotfile
            plt.savefig(phasefile)

    def plot_linear(self, frequencies=None, options=None):
        self._plot_data_amp(frequencies=frequencies,
                            linear=True, options=options)
        self._plot_data_phase(frequencies=frequencies,
                              options=options)

    def plot_log(self, frequencies=None, options=None):
        self._plot_data_amp(frequencies=frequencies,
                            linear=False, options=options)
        self._plot_data_phase(frequencies=frequencies,
                              options=options)

    

        
