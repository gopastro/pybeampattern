#from beampattern.gpib_devices.hp3457a_multimeter import Multimeter
from beampattern.gpib_devices.unidex11 import Unidex11
from beampattern.gpib_devices.hp83620a import HP83620A
from beampattern.gpib_devices.hp3478a_multimeter import Multimeter
from beampattern.serial import Fluke
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


class AzimuthMap(object):
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
        self.uni = None
        self.multimeter = None
        self.syn = None
        self.flukemeter = None
        if self.devices.use_unidex:
            try:
                self.uni = Unidex11()
                self.uni.reset()
                time.sleep(2.0)
                #self.uni.home(axis='X')
                #time.sleep(10.0)
                logger.info("Unidex 11 available, reset and homed")
            except:
                logger.error("Unidex11 Not available")
                raise BeamPatternGeneralError("open_devices", "Unidex11 Not available")
        if self.devices.use_multi:
            try:
                self.multimeter = Multimeter()
                #if self.multimeter.idstr != 'HP3457A':
                #    logger.error("Multimeter ID not right")
                #    raise BeamPatternGeneralError("open_devices", "Multimeter ID not right")
                logger.info("HP3478A multimeter initialized")
                time.sleep(0.5)
                self.multimeter.setup_ac(nplc=self.multi.nplc,
                                         range=self.multi.range,
                                         nrdgs=self.multi.nrdgs,
                                         resolution=self.multi.resolution)
                self.nrdgs = self.multi.nrdgs
            except:
                logger.error("Multimeter not available")
                raise BeamPatternGeneralError("open_devices", "Multimeter not available")
        
        if self.devices.use_synth:
            try:
                self.syn = HP83620A()
                self.syn.set_mult(self.synth.mult)
                time.sleep(0.2)
                logger.info("HP83620A synthesizer pulse mod setup")
                self.syn.setup_pulse()
                logger.info("HP83620A synthesizer available and online")
            except:
                logger.error("HP83620A not available")
                raise BeamPatternGeneralError("open_devices", "HP83620A not available")

        if self.devices.use_fluke:
            try:
                self.flukemeter = Fluke()
                logger.info("Fluke is online")
                time.sleep(0.5)
                self.nrdgs = self.fluke.nrdgs
            except:
                logger.error("Fluke 287 is not available. Error: %s" % sys.exc_info())
                raise BeamPatternGeneralError("open_devices", "Fluke 287 not available")

    def take_readings(self, nrdgs=2):
        if self.devices.use_multi:
            try:
                vmean, vstd = self.multimeter.take_readings(nrdgs=nrdgs)
                return vmean, vstd
            except:
                raise BeamPatternGeneralError("take_readings", "Cannot read HP voltmeter")
        else:
            try:
                vmean, vstd = self.flukemeter.measure(nrdgs=nrdgs)
                return vmean, vstd
            except:
                raise BeamPatternGeneralError("take_readings", "Cannot read Fluke voltmeter")
            
    def _increase_power_level(self, plevel, vmin, vmax):
        iterate = True
        new_power = plevel
        while iterate:
            new_power += 1
            if new_power > 13:
                logger.error("Power level exceeded. Setting it to 13 dBm")
                return (13)
            self.syn.set_power_level(new_power)
            time.sleep(0.2)
            #vmean, vstd = self.multimeter.take_readings(nrdgs=self.multi.nrdgs)
            vmean, vstd = self.take_readings(nrdgs=self.nrdgs)
            if vmean > vmin:
                if vmean < vmax:
                    #success
                    return new_power
                else:
                    new_power -= 0.5
                    self.syn.set_power_level(new_power)
                    time.sleep(0.2)
                    #vmean, vstd = self.multimeter.take_readings(nrdgs=self.multi.nrdgs)
                    vmean, vstd = self.take_readings(nrdgs=self.nrdgs)
                    logger.info("Current voltage is: %s" % vmean)
                    return new_power
            else:
                iterate = True

    def _decrease_power_level(self, plevel, vmin, vmax):
        iterate = True
        new_power = plevel
        while iterate:
            new_power -= 1
            if new_power < -5:
                logger.error("Power level too low. Setting it to -5 dBm")
                return (-5)
            self.syn.set_power_level(new_power)
            time.sleep(0.2)
            vmean, vstd = self.take_readings(nrdgs=self.nrdgs)
            if vmean < vmax:
                if vmean > vmin:
                    #success
                    return new_power
                else:
                    new_power += 0.5
                    self.syn.set_power_level(new_power)
                    time.sleep(0.2)
                    vmean, vstd = self.take_readings(nrdgs=self.nrdgs)
                    logger.info("Current voltage is: %s" % vmean)
                    return new_power
            else:
                iterate = True

    def check_boresight_power(self, vmin=6.0, vmax=7.0):
        """
        Adjust boresight rf power level so that the
        read voltage is between vmin and vmax, and store
        the power levels in an array
        """
        if self.offset != 0.0:
            #not already at home
            logger.info("Go to home position")
            self.uni.home(axis='X')
            logger.info("Waiting 10 seconds to be sure")
            time.sleep(10.0)
        self.rfpower = []
        for freq in self.synth.freq:
            self.syn.set_freq(freq*1e9)
            time.sleep(0.3)
            plevel = self.syn.get_power_level()
            time.sleep(2.0)
            vmean, vstd = self.take_readings(nrdgs=self.nrdgs)
            if vmean >= vmin and vmean <= vmax:
                self.rfpower.append(plevel)
            else:
                if vmean < vmin:
                    #too little power
                    plevel = self._increase_power_level(plevel, vmin, vmax)
                    self.rfpower.append(plevel)
                else:
                    #too much power
                    plevel = self._decrease_power_level(plevel, vmin, vmax)
                    self.rfpower.append(plevel)
            logger.info("For freq = %s GHz, power level needed is %s dBm" % (freq, plevel))
        logger.info("Done checking boresight power")
        
    def measure_offset(self):
        """
        Measures the zero-point offset of the meter
        """
        logger.info("Go to home position")
        self.uni.home(axis='X')
        logger.info("Waiting 10 seconds to be sure")
        time.sleep(10.0)
        logger.info("Measuring zero point offset, turning off source")
        self.syn.output_off()
        time.sleep(3.0)
        vmean, vstd = self.take_readings(nrdgs=5)
        self.offset = vmean
        self.offset_std = vstd
        logger.info("Measured offset of the voltmeter as: %s" % self.offset)
        self.syn.output_on()
        logger.info("Turning synth source back on")
        time.sleep(0.3)
        
    def make_header(self, adjust_boresight=False):
        hdr = ""
        hdr += "# Beammap Timestamp: %s\n" % self.datetime_str
        hdr += "# Configfile: %s\n" % self.cfgfile
        hdr += "# Comment: %s\n" % self.general.comment
        hdr += "# use_unidex: %s; use_multi: %s; use_synth: %s\n" % \
               (self.devices.use_unidex, self.devices.use_multi, self.devices.use_synth)
        hdr += "# Map Azimuth Params: xmin: %.2f deg; xmax: %.2f deg; xinc: %.2f deg\n" % \
               (self.azimuth.xmin, self.azimuth.xmax, self.azimuth.xinc)
        hdr += "# Map Velocity: %.2f deg/s; Slew speed: %.2f deg/s\n" % \
               (self.azimuth.xmap_vel, self.azimuth.xslew_vel)
        hdr += "# Multimeter settings: NPLC: %s; nrdgs: %d; range: %s; res: %.5g\n" % \
               (self.multi.nplc, self.multi.nrdgs, self.multi.range, self.multi.resolution)
        if self.devices.use_fluke:
            hdr += "# Fluke device: %s; nrdgs: %d\n" % \
                   (self.fluke.device, self.fluke.nrdgs)
        hdr += "# Voltage offset: %.5g +/- %.5g\n" % (self.offset, self.offset_std)
        if self.devices.use_synth:
            hdr += "# Synthesizer Multiplier: %.1f\n" % (self.synth.mult)
            hdr += "# Frequenies (GHz): %s\n" % (self.synth.freq)
            if adjust_boresight:
                hdr += "# Adjusted boresight power levels: "
                for i, freq in enumerate(self.synth.freq):
                    hdr += "f:%s GHz P:% dBm " % (freq, self.rfpower[i])
                hdr += "\n"
            hdr += "# Data columns:\n"
            hdr += "# Az"
            for freq in self.synth.freq:
                if self.nrdgs > 1:
                    hdr += ",f%.1fGHz,f%.1fGHz std" % (freq, freq)
                else:
                    hdr += ",f%.1fGHz" % freq
            hdr += "\n"
        return hdr

    def make_map(self, adjust_boresight=False, measure_ac_offset=True):
        if measure_ac_offset:
            self.measure_offset()
        if adjust_boresight:
            self.check_boresight_power()            
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
        header = self.make_header(adjust_boresight=adjust_boresight)
        fp.write(header)
        plt.ion()
        plt.plot([self.azimuth.xmin, self.azimuth.xmax], [0, 0], 'r-')
        plt.xlim(self.azimuth.xmin, self.azimuth.xmax)
        plt.ylim(-0.5, 10.0)
        plt.draw()
        for az in azimuths:
            wait = (abs(az-self.uni.pos_az)/self.azimuth.xmap_vel) + 1.0
            self.uni.set_azimuth(az, self.azimuth.xmap_vel)
            logger.info("Sleeping for %.2f seconds while stage gets to %.1f degrees" % (wait, az))
            time.sleep(wait)
            fp.write("%.3f" % az)
            for i, freq in enumerate(self.synth.freq):
                self.syn.set_freq(freq*1e9)
                time.sleep(0.1)
                if adjust_boresight:
                    self.syn.set_power_level(self.rfpower[i])
                    logger.info("For Freq: %s GHz, adjusted power level to: %s dBm" % (freq, self.rfpower[i]))
                time.sleep(0.2)
                vmean, vstd = self.take_readings(nrdgs=self.nrdgs)
                logger.info("Az: %.2f, Freq: %.3f, Voltage: %.6g +/- %.6g" % (az, freq, vmean, vstd))
                if self.nrdgs > 1:
                    fp.write(",%.6g,%.6g" % (vmean-self.offset, vstd))
                else:
                    fp.write(",%.6g,%.6g" % (vmean-self.offset))
                plt.plot(az, vmean, self.plot_symbols[i])
                plt.draw()
            fp.write('\n')
                         
        time.sleep(10.0)
        self.uni.home(axis='X')
        logger.info("Map Completed, Saving data file %s" % self.filename)
        fp.close()

                
