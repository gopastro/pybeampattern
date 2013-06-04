from beampattern.gpib_devices.hp3457a_multimeter import Multimeter
from beampattern.gpib_devices.unidex11 import Unidex11
from beampattern.gpib_devices.hp83620a import HP83620A
from beampattern.utils.beampattern_exceptions import BeamPatternGeneralError, BeamPatternArgumentError
from beampattern.logging import logger
import sys, os
import time

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
    def __init__(self, cfg, filename, datetime_str):
        self.cfg = cfg
        self._get_config_parameters()
        self.filename = filename
        self.datetime_str = datetime_str
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
        self.multi = None
        self.syn = None
        if self.devices.use_unidex:
            try:
                self.uni = Unidex11()
                self.uni.reset()
            except:
                logger.error("Unidex11 Not available")
                raise BeamPatternGeneralError("open_devices", "Unidex11 Not available")
        if self.devices.use_multi:
            try:
                self.multi = Multimeter()
                if self.multi.idstr != 'HP3457A':
                    logger.error("Multimeter ID not right")
                    raise BeamPatternGeneralError("open_devices", "Multimeter ID not right")
                logger.info("HP3457A multimeter initialized")
                time.sleep(0.5)
                self.multi.setup_ac(nplc=self.multi.nplc,
                                    range=self.multi.range,
                                    nrdgs=self.multi.nrdgs,
                                    resolution=self.multi.resolution)
            except:
                logger.error("Multimeter not available")
                raise BeamPatternGeneralError("open_devices", "Multimeter not available")

        if self.devices.use_synth:
            try:
                self.syn = HP83620A()
                self.syn.set_mult(self.synth.mult)
            except:
                logger.error("HP83620A not available")
                raise BeamPatternGeneralError("open_devices", "HP83620A not available")
