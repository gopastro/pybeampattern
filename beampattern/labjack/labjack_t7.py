from labjack import ljm
from beampattern.utils.beampattern_exceptions import BeamPatternArgumentError

class LabJackT7(object):
    def __init__(self, debug=True):
        self.handle = ljm.openS("ANY", "ANY", "ANY")
        self.info = ljm.getHandleInfo(handle)
        if debug:
            print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
                  "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
                  (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

    def digital_output(self, channel, level):
        if channel not in range(8):
            raise BeamPatternArgumentError("LabJack T7", "channel should be >= 0 and <8")
        if level not in (0, 1):
            raise BeamPatternArgumentError("LabJack T7", "level should be 0 or 1")
        ljm.eWriteName(self.handle, 'FIO%1d' % channel, level)

            
