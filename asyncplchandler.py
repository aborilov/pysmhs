from twisted.internet import serialport, reactor
from twisted.internet.protocol import ClientFactory
from pymodbus.factory import ClientDecoder
from pymodbus.client.async import ModbusClientProtocol
from serial import PARITY_NONE, PARITY_EVEN, PARITY_ODD
from serial import STOPBITS_ONE, STOPBITS_TWO
from serial import FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS
from pymodbus.transaction import ModbusAsciiFramer as ModbusFramer

from abstracthandler import AbstractHandler
from pydispatch import dispatcher


class SMHSProtocol(ModbusClientProtocol):

    def __init__(self, framer, pol_list, logger, reader):
        ''' Initializes our custom protocol

        :param framer: The decoder to use to process messages
        :param endpoint: The endpoint to send results to
        '''
        ModbusClientProtocol.__init__(self, framer)
        self.pol_list = pol_list
        self.logger = logger
        self.reader = reader
        self.logger.debug("Beggining the processing loop")
        reactor.callLater(3, self.fetch_holding_registers)

    def fetch_holding_registers(self):
        for t in self.pol_list:
            if t in ["inputc"]:
                address_map = self.pol_list[t]
                for registers in address_map:
                    self.logger.error("Read registers: %s" % (registers,))
                    d = self.read_holding_registers(*registers)
                    d.addCallback(self.start_next_cycle, register=registers)
                    d.addErrback(self.error_handler)

    def start_next_cycle(self, response, register):
        self.logger.error("readed register %s" % (register,))
        val = {}
        for i in range(0, register[1] - 1):
            val[register[0] + i] = response.getRegister(i)
        self.reader(val)
        reactor.callLater(3, self.fetch_holding_registers)

    def error_handler(self, failure):
        self.logger.error(failure)


class SMHSFactory(ClientFactory):

    protocol = SMHSProtocol

    def __init__(self, framer, pol_list, logger, reader):
        self.framer = framer
        self.pol_list = pol_list
        self.logger = logger
        self.reader = reader

    def buildProtocol(self, _):
        proto = self.protocol(
            self.framer, self.pol_list, self.logger, self.reader)
        proto.factory = self
        return proto


class SerialModbusClient(serialport.SerialPort):

    def __init__(self, factory, *args, **kwargs):
        protocol = factory.buildProtocol(None)
        self.decoder = ClientDecoder()
        serialport.SerialPort.__init__(self, protocol, *args, **kwargs)


class asyncplchandler(AbstractHandler):

    def __init__(self, parent=None, params={}):
        AbstractHandler.__init__(self, parent, params)
        self.logger.info("Init async_plchandler")
        serverconfig = params["server"]
        self.serial_port = params["port"]
        self.pollint = serverconfig["pollingTimeout"]
        self.packetSize = int(serverconfig["packetSize"])
        self.tagslist = {}
        #fill tagslist with tags from all types
        for tagtype in self.config:
            self.tagslist.update(self.config[tagtype])
        #fill address list
        self.fullAddressList = {}
        for x in self.tagslist:
            if "address" in self.tagslist[x]:
                address = self.tagslist[x]["address"]
                self.fullAddressList[address] = x

    def _generate_address_map(self, addressList):
        '''
        generate addressMap based on the addressList
        addressMap is dictionary with key = startaddress to read
        and value = number of bits need to read
        '''
        keylist = addressList.keys()
        maxAddress = int(max(keylist))
        minAddress = int(min(keylist))
        s = maxAddress - minAddress + 1
        c, d = divmod(s, self.packetSize)
        l = maxAddress - d + 1
        addressMap = []
        for x in range(0, c):
            curAddress = minAddress + self.packetSize * x
            addressMap.append((curAddress, self.packetSize,))
        if (d > 0):
            addressMap.append((l, d,))
        return tuple(addressMap)

    def reader(self, register):
        for addr in register:
            self.logger.error("in plchandler %d:%d" % (addr, register[addr]))

    def run(self):
        AbstractHandler.run(self)
        framer = ModbusFramer(ClientDecoder())
        pol_list = {}
        for t in self.config.keys():
            if t in ["output", "input", "inputc"]:
                address_list = {}
                for x in self.config[t]:
                    address = self.tagslist[x]["address"]
                    address_list[address] = x
                pol_list[t] = self._generate_address_map(address_list)
        factory = SMHSFactory(framer, pol_list, self.logger, self.reader)
        SerialModbusClient(
            factory, "/dev/plc",
            reactor, baudrate=9600,
            parity=PARITY_EVEN, bytesize=SEVENBITS,
            stopbits=STOPBITS_TWO, timeout=3)

    def stop(self):
        AbstractHandler.stop(self)
