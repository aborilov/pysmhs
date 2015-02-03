import logging

from twisted.internet import serialport, reactor
from twisted.internet import defer
from twisted.internet.protocol import ClientFactory

from pymodbus.factory import ClientDecoder
from pymodbus.client.async import ModbusClientProtocol
from pymodbus.transaction import ModbusAsciiFramer as ModbusFramer

from serial import PARITY_NONE, PARITY_EVEN, PARITY_ODD
from serial import STOPBITS_ONE, STOPBITS_TWO
from serial import FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS

from abstracthandler import AbstractHandler

logger = logging.getLogger()

pymodbus_logger = logging.getLogger('pymodbus')
pymodbus_logger.setLevel(logging.ERROR)

class SMHSProtocol(ModbusClientProtocol):

    def __init__(self, framer, pol_list, reader, writepool):
        ''' Initializes our custom protocol

        :param framer: The decoder to use to process messages
        :param endpoint: The endpoint to send results to
        '''
        ModbusClientProtocol.__init__(self, framer)
        self.pol_list = pol_list
        self.reader = reader
        self.writepool = writepool
        logger.debug("Begining the processing loop")

    def connectionMade(self):
        logger.debug("Connected to ModBus")
        super(SMHSProtocol, self).connectionMade()
        self.read_reg()

    @defer.inlineCallbacks
    def read_reg(self):
        #Write counter threshold
        reg = (4598, 1)
        yield self.read_holding_registers(*reg)
        #Write polling tag
        # yield self.write_coil(2057, 0xFF00)
        while (1):
            try:
                yield self.fetch_holding_registers()
            except Exception as e:
                logger.exception('')

    @defer.inlineCallbacks
    def fetch_holding_registers(self):
        address_map = self.pol_list["inputc"]
        for register in address_map:
            response = yield self.read_holding_registers(*register)
            val = {}
            for i in range(0, register[1]):
                val[register[0] + i] = response.getRegister(i)
            self.reader(val, "inputc")

        address_map = self.pol_list["output"]
        for register in address_map:
            response = yield self.read_coils(*register)
            val = {}
            for i in range(0, register[1]):
                val[register[0] + i] = response.getBit(i)
            self.reader(val, "output")

    # def write_tags(self, response):
        # d = None
        # if len(self.writepool):
            # logger.debug("writepool len = %d" % len(self.writepool))
            # for x in self.writepool.keys():
                # val = int(self.writepool.pop(x))
                # logger.debug(
                    # "writting tag %s to %d" % (x, val))
                # if val:
                    # val = 0xFF00
                # else:
                    # val = 0x0000
                # if not d:
                    # d = self.write_tag(response, x, val)
                # else:
                    # d.addCallback(self.write_tag, addr=x, value=val)
        # if not d:
            # self.write_polling_tag(response)
        # else:
            # d.addCallback(self.write_polling_tag)

    # def write_tag(self, response, addr, value):
        # return self.write_coil(addr, value)


class SMHSFactory(ClientFactory):

    protocol = SMHSProtocol

    def __init__(self, framer, pol_list, reader, writepool):
        self.framer = framer
        self.pol_list = pol_list
        self.reader = reader
        self.writepool = writepool

    def buildProtocol(self, _):
        proto = self.protocol(
            self.framer,
            self.pol_list, self.reader, self.writepool)
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
        logger.info("Init async_plchandler")
        serverconfig = params["server"]
        self.serial_port = params["port"]
        self.pollint = serverconfig["pollingTimeout"]
        self.packetSize = int(serverconfig["packetSize"])
        self.tagslist = {}
        self.writepool = {}
        self._inputctags = {}
        self._inputtag_threshold = int(serverconfig["counter_threshold"])
        #fill tagslist with tags from all types
        for tagtype in self.config:
            self.tagslist.update(self.config[tagtype])
        #fill address list
        self.full_address_list = {}
        for x in self.tagslist:
            if "address" in self.tagslist[x]:
                address = self.tagslist[x]["address"]
                self.full_address_list[int(address)] = x
        logger.debug("Full address list - %s" % self.full_address_list)

    def _settag(self, name, value):
        logger.debug("set tag %s to %s" % (name, value))
        self.writepool[int(self.tagslist[name]["address"])] = value

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
                    self.sendevents(tag, value)
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
                    for x in range(lastval + 1, value + 1):
                        self.sendevents(tag, x & 1)
                else:
                    dif = self._inputtag_threshold - lastval + value
                    for x in range(lastval + 1, lastval + dif + 1):
                        self.sendevents(tag, x & 1)

        self._inputctags[tag] = value
        self._tags[tag] = value & 1

    def start(self):
        AbstractHandler.start(self)
        framer = ModbusFramer(ClientDecoder())
        pol_list = {}
        for t in self.config.keys():
            if t in ["output", "input", "inputc"]:
                address_list = {}
                for x in self.config[t]:
                    address = self.tagslist[x]["address"]
                    address_list[address] = x
                pol_list[t] = self._generate_address_map(address_list)
        factory = SMHSFactory(
            framer, pol_list, self.reader, self.writepool)
        SerialModbusClient(
            factory, "/dev/plc",
            reactor, baudrate=9600,
            parity=PARITY_EVEN, bytesize=SEVENBITS,
            stopbits=STOPBITS_TWO, timeout=0)

    def stop(self):
        AbstractHandler.stop(self)
