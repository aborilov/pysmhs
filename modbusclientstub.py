'''
Created on Jan 12, 2012

@author: pavel
'''


class ModbusClientStub(object):

    coils = {}

    for i in range(1280, 2057):
        coils[str(i)] = False

    for i in range(1040, 1056):
        coils[str(i)] = False

    for i in range(3590, 3610):
        coils[str(i)] = False
    coils["3640"] = "14"

    def connect(self):
        print "Connecting to ModBus"

    def read_address(self, address, count):
#        print "read address "+address
        rv = ""
        for i in range(int(count)):
            if self.coils[str(int(address) + i)]:
                rv += "1"
            else:
                rv += "0"
        return rv

    def read_register(self, address, count=1):
        rv = ""
        for i in range(int(count)):
            if self.coils[str(int(address) + i)]:
                rv += "1"
            else:
                rv += "0"
        return rv

    def write(self, address, value):
        self.coils[address] = value
#        print "write to "+address+" : "+str(value)

    def disconnect(self):
        print "disconnect"
