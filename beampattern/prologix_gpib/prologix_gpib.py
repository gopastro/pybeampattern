import socket
import time

class PrologixGPIB(object):
    """
    A GPIB Base class for the Prologix Ethernet based
    GPIB device
    """
    def __init__(self, host="192.168.2.100",
                 port=1234):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

    def set_gpib_address(self, gpib_address):
        self.sock.send('++addr %d\n' % gpib_address)
        # put in auto 0 mode
        self.sock.send('++auto 0\n')

    def ask(self, msg, readlen=128):
        """Send and receive something"""
        self.sock.send('%s\n' % msg)
        self.sock.send('++read eoi\n')
        ret = self.sock.recv(readlen)
        return ret.strip()

    def write(self, msg):
        """Send something"""
        self.sock.send('%s\n' % msg)

    def idstring(self):
        """returns ID String"""
        ids = self.ask('*IDN?')
        return ids        

    def close(self):
        self.sock.close()
        
