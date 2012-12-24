

class SMHSProtocol(ModbusClientProtocol):

    def __init__(self, framer, endpoint):
        ''' Initializes our custom protocol

        :param framer: The decoder to use to process messages
        :param endpoint: The endpoint to send results to
        '''
        ModbusClientProtocol.__init__(
            self, framer, pol_list, addr_list)
        self.endpoint = endpoint
        self.pol_list = pol_list
        self.addr_list = addr_list
        log.debug("Beggining the processing loop")
        reactor.callLater(CLIENT_DELAY, self.fetch_holding_registers)

    def fetch_holding_registers(self):
        for registers in self.pol_list:
            d = self.read_holding_registers(*registers)
            d.addCallBacks(self.6)
