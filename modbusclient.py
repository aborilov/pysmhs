'''
Created on Jan 12, 2012

@author: pavel
'''
from pymodbus.client.sync import ModbusSerialClient as Modbus


class ModbusClient(object):

    def __init__(self, port):
        self.port = port

    def connect(self):
        method = 'ascii'
        conf = {'port': self.port['name']}
        conf['baudrate'] = self.port['speed']
        conf['bytesize'] = int(self.port['data_length'])
        conf['parity'] = self.port['parity']
        conf['timeout'] = float(self.port['timeout'])
        conf['stopbits'] = int(self.port['stop_bits'])
        print "connect to " + self.port['name']
        self.client = Modbus(method='ascii', **conf)
        self.client.connect()
        print "Connecting to ModBus"

    def read_address(self, address, count=1):
        rr = self.client.read_discrete_inputs(int(address), int(count))
        rv = []
        rv = list(rr.bits)
        return rv

    def read_register(self, address, count=1):
        rr = self.client.read_holding_registers(int(address), int(count))
        rv = []
        rv = list(rr.registers)
        return rv

    def write(self, address, value):
        self.client.write_coil(int(address), int(value))
        #print "write to "+address+" : "+str(value)

    def disconnect(self):
        print "disconnect"
        self.client.close()
