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
        self.rr_count = 0
        self.logger.debug("Begining the processing loop")
        reactor.callLater(3, self.fetch_holding_registers)

    def fetch_holding_registers(self):
        for t in self.pol_list:
            self.logger.debug("have type = %s" % t)
            if t in ["inputc"]:
                address_map = self.pol_list[t]
                for registers in address_map:
                    self.logger.error("Read registers: %s" % (registers,))
                    self.rr_count += 1
                    d = self.read_holding_registers(*registers)
                    d.addCallback(
                        self.send_registers, register=registers, t=t)
                    d.addErrback(self.error_handler)

    def fetch_coils(self):
        for t in self.pol_list:
            self.logger.debug("have type = %s" % t)
            if t in ["input", "output"]:
                address_map = self.pol_list[t]
                for registers in address_map:
                    self.logger.error("Read coil: %s" % (registers,))
                    self.rr_count += 1
                    d = self.read_coils(*registers)
                    d.addCallback(self.send_coils, register=registers, t=t)
                    d.addErrback(self.error_handler)

    def send_coils(self, response, register, t):
        self.logger.error("readed coils %s" % (register,))
        val = {}
        for i in range(0, register[1] - 1):
            val[register[0] + i] = response.getBit(i)
        self.reader(val, t)
        self.rr_count -= 1
        self.logger.error("count=%d" % self.rr_count)
        if not self.rr_count:
            reactor.callLater(3, self.fetch_holding_registers)

    def send_registers(self, response, register, t):
        self.logger.error("readed register %s" % (register,))
        val = {}
        for i in range(0, register[1] - 1):
            val[register[0] + i] = response.getRegister(i)
        self.reader(val, t)
        self.rr_count -= 1
        self.logger.error("count=%d" % self.rr_count)
        if not self.rr_count:
            reactor.callLater(3, self.fetch_coils)

    def error_handler(self, failure):
        self.logger.error(failure)
        self.rr_count -= 1


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


class plchandler(AbstractHandler):

    def __init__(self, parent=None, params={}):
        AbstractHandler.__init__(self, parent, params)
        self.logger.info("Init async_plchandler")
        serverconfig = params["server"]
        self.serial_port = params["port"]
        self.pollint = serverconfig["pollingTimeout"]
        self.packetSize = int(serverconfig["packetSize"])
        self.tagslist = {}
        self._inputctags = {}
        #fill tagslist with tags from all types
        for tagtype in self.config:
            self.tagslist.update(self.config[tagtype])
        #fill address list
        self.full_address_list = {}
        for x in self.tagslist:
            if "address" in self.tagslist[x]:
                address = self.tagslist[x]["address"]
                self.full_address_list[int(address)] = x
        self.logger.debug("Full address list - %s" % self.full_address_list)

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

    def reader(self, register, t):
        for addr in register:
            if addr in self.full_address_list:
                tagname = self.full_address_list[addr]
                tagstate = int(register[addr])
                if t == "inputc":
                    self.__addinputctag(tagname, tagstate)
                else:
                    self.__addtag(tagname, tagstate)
                self.logger.error(
                    "in plchandler %s:%d" %
                    (self.full_address_list[addr], register[addr]))

    def __addtag(self, tag, value, addevent=True):
        '''
        check if this tag in polling cache
        and if not add it
        and if tag change it value since last pooling
        add it to events list
        '''
        if tag in self._tags:
            if self._tags[tag] != value:
                self._tags[tag] = value
                if addevent:
                    # self.events[tag] = value
                    self.events.append({"tag": tag, "value": value})
        else:
            self._tags[tag] = value

    def __addinputctag(self, tag, value):
        '''
        add event for input registers
        count diff from last value and send value
        this tag would produce as normal input tag
        '''
        if tag in self._inputctags:
            lastval = self._inputctags[tag]
            if lastval != value:
                if value > lastval:
                    dif = value - lastval
                    for x in range(lastval + 1, value + 1):
                        self.events.append({"tag": tag, "value": x & 1})
        self._inputctags[tag] = value
        self._tags[tag] = value & 1

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
