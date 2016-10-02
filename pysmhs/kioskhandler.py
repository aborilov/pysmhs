from abstracthandler import AbstractHandler

import logging

logger = logging.getLogger()

from louie import dispatcher
from serial import EIGHTBITS
from serial import PARITY_NONE
from serial import STOPBITS_ONE
from twisted.internet import reactor
from twisted.internet.serialport import SerialPort

logger_tr = logging.getLogger('transitions.core')
logger_tr.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(
    'transition.log', maxBytes=1028576, backupCount=10)
form = logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)s:%(message)s')
handler.setFormatter(form)
logger_tr.addHandler(handler)


from transitions import Machine
from pymdb.device.bill_validator import BillValidator
from pymdb.device.changer import Changer, COINT_ROUTING
from pymdb.protocol.mdb import MDB

from fsm.changer_fsm import ChangerFSM
from fsm.cash_fsm import CashFSM
from fsm.validator_fsm import BillValidatorFSM
from fsm.kiosk_fsm import KioskFSM


COINS = {
    0: 1,
    1: 2,
    2: 5,
    4: 10
}

class RUChanger(Changer):

    def __init__(self, proto):
        super(RUChanger, self).__init__(proto, COINS)

    def dispense_all(self):
    #logger.debug("coin_count:  0x%0.2X" % self.coin_count[2])
        self.dispense(coin=0, count=10)
        self.dispense(coin=1, count=10)
        self.dispense(coin=2, count=10)
        self.dispense(coin=4, count=10)



BILLS = {
    0: 10,
    1: 50,
    2: 100
}

class RUBillValidator(BillValidator):

    def __init__(self, proto):
        super(RUBillValidator, self).__init__(proto, BILLS)


class Plc(object):

    def __init__(self):
        self.prepare_time_sec = 1
        self.prepare_success = True

    def prepare(self, product):
        print('prepare'.format(product))
        if self.prepare_success:
            reactor.callLater(self.prepare_time_sec, self.fire_prepared)
        else:
            reactor.callLater(self.prepare_time_sec, self.fire_not_prepared)

    def fire_prepared(self):
        dispatcher.send_minimal(
            sender=self, signal='prepared')

    def fire_not_prepared(self):
        dispatcher.send_minimal(
            sender=self, signal='not_prepared')


class ValidatorStub():
    def start_accept(self):
        pass

    def stop_accept(self):
        pass

    def start_device(self):
        pass

    def stop_device(self):
        pass

    def stack_bill(self):
        pass

    def return_bill(self):
        pass

    def get_total_amount(self):
        return 0

    def initialize(self):
        dispatcher.send_minimal(
            sender=self, signal='online')
        dispatcher.send_minimal(
            sender=self, signal='initialized')



PRODUCTS = {
    1: 11,
    2: 19
    }

class kioskhandler(AbstractHandler):

    def __init__(self, parent=None, params={}):
        logger.info("Init kiosk handler")
        self.proto = MDB()
        self.changer = RUChanger(proto=self.proto)

#     validator = RUBillValidator(proto=self.proto)
        self.validator = ValidatorStub()

        self.plc = Plc()
        self.changer_fsm = ChangerFSM(changer=self.changer)
        self.validator_fsm = BillValidatorFSM(validator=self.validator)
        self.cash_fsm = CashFSM(changer_fsm=self.changer_fsm, validator_fsm=self.validator_fsm)
        self.kiosk_fsm = KioskFSM(self.plc, cash_fsm=self.cash_fsm, products=PRODUCTS)
        AbstractHandler.__init__(self, parent, params)

    def start(self):
        AbstractHandler.start(self)
        SerialPort(
            #  self.proto, '/dev/ttyUSB0', reactor,
            self.proto, '/dev/ttyMDB', reactor,
            baudrate='38400', parity=PARITY_NONE,
            bytesize=EIGHTBITS, stopbits=STOPBITS_ONE)
        reactor.callLater(0, self.kiosk_fsm.start)
        reactor.callLater(0.2, self.validator.initialize)
        dispatcher.connect(self.total_process, signal='total_amount_changed')
        #  dispatcher.connect(self.deposit_process, signal='deposit_amount_changed')

    def total_process(self, amount):
        self.settag('total', amount)

    def deposit_process(self, amount):
        logger.debug('deposit process : {}'.format(amount))
        self.settag('deposit', amount)

    def loadtags(self):
        amount = self.kiosk_fsm.get_total_amount()
        self._tags['total'] = amount
        #  self._tags['deposit'] = 0

    def process(self, signal, event):
        if signal == 'plchandler':
            if 'GREEN' in event and event['GREEN'] == 1:
                logger.debug("START")
                self.kiosk_fsm.sell(product=1)
            elif 'RED1' in event and event['RED1'] == 1:
                self.kiosk_fsm.sell(product=2)
            elif 'RED2' in event and event['RED2'] == 1:
                self.changer.dispense_amount(100)
