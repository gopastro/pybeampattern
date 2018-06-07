from beampattern.prologixgpib.unidex11 import Unidex11
from beampattern.prologixgpib.hp83620a import HP83620A
from beampattern.prologixgpib.prologix_gpib import PrologixGPIB
from beampattern.prologixgpib.vector_voltmeter import VectorVoltmeter
from beampattern.utils.beampattern_exceptions import BeamPatternGeneralError, BeamPatternArgumentError
from beampattern.logging import logger
import matplotlib.pyplot as plt

import sys, os
import time
import numpy

logger.name = __name__


class ConfigObj(object):
    def __init__(self):
        pass


class AzimuthVectorMap(object):
    """
    Given a config object dictionary cfg, and a filename to
    write output data to and a datetime_str, this class
    check for correct configuration and does a map
    """
    def __init__(self, cfg, filename, datetime_str, cfgfile):
        self.plot_symbols = ['o', 's', 'v', '^', '<', '>',
                             '1', '2', '3', '4', 'p', '*',
                             'h', 'H', '+', 'x', 'D', 'd']
                             
        self.cfg = cfg
        self._get_config_parameters()
        self.filename = filename
        self.datetime_str = datetime_str
        self.cfgfile = cfgfile
        self.freq_list = []
        self.offset = 0.0
        self.offset_std = 0.0
        self.nrdgs = 1
        if not self.check_map_azimuth_parameters():
            logger.error("Map Parameters Malformed")
            raise BeamPatternGeneralError("AzimuthMap", "Map Parameters Malformed")

    def _get_config_parameters(self):
        for key, val in self.cfg.items():
            setattr(self, key, ConfigObj())
            obj = getattr(self, key)
            for k, v in val.items():
                setattr(obj, k, v)

    def check_map_azimuth_parameters(self):
        if self.azimuth.xmin < -180.0:
            logger.error("xmin is set to %s, and is less than -180 degrees. Please fix" % self.azimuth.xmin)
            return False
        if self.azimuth.xmax > 180.0:
            logger.error("xmax is set to %s, and is greater than 180 degrees. Please fix" % self.azimuth.xmax)
            return False
        return True

    def open_devices(self):
        self.prologix = PrologixGPIB()
        self.vv = None
        self.syn = HP83620A(self.prologix)
        self.freq_list = numpy.array(self.synthesizer.freq)/1.e9
        if self.devices.use_unidex:
            try:
                self.uni = Unidex11(self.prologix)
                self.uni.reset()
                time.sleep(2.0)
                self.uni.home(axis='X')
                time.sleep(10.0)
                logger.info("Unidex 11 available, reset and homed")
            except:
                logger.error("Unidex11 Not available")
                raise BeamPatternGeneralError("open_devices", "Unidex11 Not available")
        if self.devices.use_vv:
            try:
                self.vv = VectorVoltmeter(self.prologix)
                logger.info("Vector network analyzer initialized")
                self.average = self.vector_voltmeter.avg_value
                time.sleep(0.5)
            except:
                logger.error("Vector Voltmeter not available")
                raise BeamPatternGeneralError("open_devices", "VNA not available")

    def take_readings(self):
        if self.devices.use_vv:
            try:
                data = self.vv.measure_transmission_single(average=self.average)
                return data
            except:
                raise BeamPatternGeneralError("take_readings", "Cannot read Vector Voltmeter")
            
        
    def make_header(self):
        hdr = ""
        hdr += "# Beammap Timestamp: %s\n" % self.datetime_str
        hdr += "# Configfile: %s\n" % self.cfgfile
        hdr += "# Comment: %s\n" % self.general.comment
        hdr += "# use_unidex: %s; use_vna: %s\n" % \
               (self.devices.use_unidex, self.devices.use_vna)
        hdr += "# Map Azimuth Params: xmin: %.2f deg; xmax: %.2f deg; xinc: %.2f deg\n" % \
               (self.azimuth.xmin, self.azimuth.xmax, self.azimuth.xinc)
        hdr += "# Map Velocity: %.2f deg/s; Slew speed: %.2f deg/s\n" % \
               (self.azimuth.xmap_vel, self.azimuth.xslew_vel)
        hdr += "# Freq_list: %s\n" % (self.freq_list/1e9)
        return hdr

    def make_map(self):
        self.uni.home(axis='X')
        time.sleep(10.0)
        azimuths = []
        for x in numpy.arange(self.azimuth.xmin, self.azimuth.xmax + self.azimuth.xinc,
                              self.azimuth.xinc):
            if x > self.azimuth.xmax:
                x = self.azimuth.xmax
            azimuths.append(x)
        azimuths = numpy.array(azimuths)
        wait = (abs(azimuths[0]-self.uni.pos_az)/self.azimuth.xslew_vel) + 1.0
        self.uni.set_azimuth(azimuths[0], self.azimuth.xslew_vel)
        logger.info("Sleeping for %.2f seconds while stage gets to start of map" % wait)
        time.sleep(wait)

        fp = open(self.filename, 'w')
        header = self.make_header()
        fp.write(header)
        plt.ion()
        plt.plot([self.azimuth.xmin, self.azimuth.xmax], [0, 0], 'r-')
        plt.xlim(self.azimuth.xmin, self.azimuth.xmax)
        plt.ylim(-0.001, 0.007)
        plt.draw()
        for az in azimuths:
            wait = (abs(az-self.uni.pos_az)/self.azimuth.xmap_vel) + 1.0
            self.uni.set_azimuth(az, self.azimuth.xmap_vel)
            logger.info("Sleeping for %.2f seconds while stage gets to %.1f degrees" % (wait, az))
            time.sleep(wait)
            fp.write("%.3f" % az)
            data = self.take_readings()
            for freq in self.freq_list:
                self.syn.set_freq(freq)
                time.sleep(0.020)
                ratio, phase = self.vv.measure_transmission_single(self.average)
                fp.write(",%.6g,%.6g" % (ratio, phase))
                logger.info("Az: %.2f, Freq: %.3f, Ratio: %g; Phase: %g" % (az, freq/1e9, ratio, phase))
                plt.plot(az, ratio, self.plot_symbols[i])
                plt.draw()
            fp.write('\n')
                         
        time.sleep(10.0)
        self.uni.home(axis='X')
        logger.info("Map Completed, Saving data file %s" % self.filename)
        fp.close()

                
