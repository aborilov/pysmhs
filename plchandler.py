'''
'''
from abstracthandler import AbstractHandler
from pydispatch import dispatcher
import time
from modbusclient import ModbusClient
from modbusclientstub import ModbusClientStub


class plchandler(AbstractHandler):
    """PLC handler"""

    def __init__(self, parent=None, params={}):
        AbstractHandler.__init__(self, parent, params)
        self.logger.info("Init plc handler")
        self.stopFlag = False
        self.writepool = {}
        self._inputctags = {}
        serverconfig = params["server"]
        self.polling = serverconfig["pollingTimeout"]
        self.packetSize = int(serverconfig["packetSize"])
        self.tagslist = {}
        for tagtype in self.config:
            self.tagslist.update(self.config[tagtype])

        if (serverconfig['fakeserver'] == '1'):
            self.mClient = ModbusClientStub()
        else:
            self.mClient = ModbusClient(params["port"])
        self.mClient.connect()

    def write_polling_tag(self):
        self._settag_by_name("pollingTag", 1)

    def writetags(self):
        '''
        save tag, that need to send to controller to pool
        and send it in run method
        '''
        #FIXME Write pool of tags
        for x in self.writepool.keys():
            self._settag_by_name(x, self.writepool.pop(x))

    def _settag(self, name, value):
        self.logger.debug("set tag %s to %s" % (name, value))
        self.writepool[name] = value

    def invertTag(self, name):
        '''
        invert binary value of tag
        if current tag value = 1, then set to 0
        and vice versa
        @param name:
        '''
        if name in self._tags:
            if self._tags[name] == 0:
                self.settag(name, 1)
            else:
                self.settag(name, 0)

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
        addressMap = {}
        for x in range(0, c):
            curAddress = minAddress + self.packetSize * x
            addressMap[curAddress] = self.packetSize
        if (d > 0):
            addressMap[l] = d
        return addressMap

    def run(self):
        '''
        Thread for polling, sending tags and events
        '''
        AbstractHandler.run(self)
        self.stopFlag = False
        fullAddressList = {}
        for x in self.tagslist:
            if "address" in self.tagslist[x]:
                address = self.tagslist[x]["address"]
                fullAddressList[address] = x
        pollingList = {}
        for t in self.config.keys():
            if t == "output" or t == "input" or t == "inputc":
                addressList = {}
                for x in self.config[t]:
                    address = self.tagslist[x]["address"]
                    addressList[address] = x
                addressMap = self._generate_address_map(addressList)
                pollingList[t] = addressMap
        self.logger.debug("Polling list - %s" % pollingList)
        while not self.stopFlag:
            #TODO write count coils in one packet
            self.writetags()
            self.write_polling_tag()
            for t in pollingList:
                addressMap = pollingList[t]
                for curAddress in addressMap:
                    if t == "inputc":
                        value \
                            = self._get_register_by_address(
                                str(curAddress), addressMap[curAddress])
                    else:
                        value \
                            = self._get_tag_by_address(
                                str(curAddress), addressMap[curAddress])
                    for v in range(len(value)):
                        if str(curAddress + v) in fullAddressList:
                            tagname = fullAddressList[str(curAddress + v)]
                            tagstate = int(value[v])
                            if t == "inputc":
                                self.__addinputctag(tagname, tagstate)
                            else:
                                self.__addtag(tagname, tagstate)
            #reading data registers
            # for x in self.config["data"]:
            #     value = self._gettag_by_name(x)
            #     self.__addtag(x, value, False)

            self.sendevents()
            time.sleep(float(self.polling))

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

    def stop(self):
        '''
        stop this thread
        modbus server
        and call stop on all handlers
        '''
        AbstractHandler.stop(self)
        self.stopFlag = True
        self.mClient.disconnect()

    def _gettag_by_name(self, name):
        address = self.tagslist[name]["address"]
        size = self.tagslist[name]["size"]
        return self.mClient.read_address(address, size)

    def _get_tag_by_address(self, address, size=1):
        return self.mClient.read_address(address, size)

    def _get_register_by_address(self, address, size=1):
        return self.mClient.read_input_regis

    def _get_register_by_address(self, address, count=1):
        return self.mClient.read_register(address, count)

    def _settag_by_name(self, name, value):
        self.mClient.write(self.tagslist[name]["address"], value)
