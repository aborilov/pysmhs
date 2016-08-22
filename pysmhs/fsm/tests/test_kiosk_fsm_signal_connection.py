from louie import dispatcher

from unittest import TestCase

from pysmhs.fsm.kiosk_fsm import KioskFSM

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock
    

class TestKioskFsm(TestCase):
    
    def setUp(self):
        self.cash_fsm = MagicMock()
        self.plc = MagicMock()
        self.products = MagicMock()

        self.mock = MagicMock()
        self.mock.cash_fsm_error = MagicMock(spec="cash_fsm_error")
        self.mock.cash_fsm_ready = MagicMock(spec="cash_fsm_ready")
        self.mock.amount_not_accepted = MagicMock(spec="amount_not_accepted")
        self.mock.amount_accepted = MagicMock(spec="amount_accepted")
        self.mock.amount_dispensed = MagicMock(spec="amount_dispensed")
        self.mock.prepared = MagicMock(spec="prepared")
        self.mock.not_prepared = MagicMock(spec="not_prepared")
        self.mock._dispense_amount_changed = MagicMock(spec="_dispense_amount_changed")
        self.mock._deposit_amount_changed = MagicMock(spec="_deposit_amount_changed")
        self.mock._total_amount_changed = MagicMock(spec="_total_amount_changed")
        self.mock._coin_amount_changed = MagicMock(spec="_coin_amount_changed")
        self.mock._bill_amount_changed = MagicMock(spec="_bill_amount_changed")
        self.mock._bill_count_changed = MagicMock(spec="_bill_count_changed")
        self.mock._coin_in = MagicMock(spec="_coin_in")
        self.mock._bill_in = MagicMock(spec="_bill_in")
        
        self.fsm = KioskFSM(cash_fsm=self.cash_fsm,
                           plc=self.plc,
                           products=self.products)
        self.fsm._connect_input_signals(cash_fsm=self.cash_fsm,
                                        plc=self.plc,
                                        receiver=self.mock)
        
    def tearDown(self):
        pass

    def test_1_connect_receiver_to_sender(self):
        '''
        test that method _connect_receiver_to_sender is called on
        kiosk_fsm initialized
        '''
        kiosk_fsm_stub = KioskFSMStub(cash_fsm=self.cash_fsm,
                                      plc=self.plc,
                                      products=self.products)
        
        self.assertEquals([({'cash_fsm':self.cash_fsm,
                             'plc':self.plc,
                             'receiver':kiosk_fsm_stub},)],
                  kiosk_fsm_stub.mock._connect_input_signals.call_args_list)

    def test_1_connection_by_cash_error(self):
        '''
        test connection between cash_fsm and kiosk_fsm by signal 'error'
        '''
        dispatcher.send_minimal(sender=self.cash_fsm, signal='error',
                                error_code='code',
                                error_text='text')
        
        self.assertEquals([({'error_code':'code',
                             'error_text':'text',},)],
                          self.mock.cash_fsm_error.call_args_list)

    def test_2_connection_by_cash_ready(self):
        '''
        test connection between cash_fsm and kiosk_fsm by signal 'ready'
        '''
        dispatcher.send_minimal(sender=self.cash_fsm, signal='ready')
        
        self.assertEquals([()], self.mock.cash_fsm_ready.call_args_list)

    def test_3_connection_by_amount_not_accepted(self):
        '''
        test connection between cash_fsm and kiosk_fsm by signal
        'not_accepted'
        '''
        dispatcher.send_minimal(sender=self.cash_fsm,
                                signal='not_accepted',
                                amount=10)
        
        self.assertEquals([({'amount':10,},)],
                          self.mock.amount_not_accepted.call_args_list)

    def test_4_connection_by_amount_accepted(self):
        '''
        test connection between cash_fsm and kiosk_fsm by signal
        'accepted'
        '''
        dispatcher.send_minimal(sender=self.cash_fsm,
                                signal='accepted',
                                amount=10)
        
        self.assertEquals([({'amount':10,},)],
                          self.mock.amount_accepted.call_args_list)

    def test_5_connection_by_amount_dispensed(self):
        '''
        test connection between cash_fsm and kiosk_fsm by signal
        'dispensed'
        '''
        dispatcher.send_minimal(sender=self.cash_fsm,
                                signal='dispensed',
                                amount=10)
        
        self.assertEquals([({'amount':10,},)],
                          self.mock.amount_dispensed.call_args_list)

    def test_6_connection_by_prepared(self):
        '''
        test connection between plc and kiosk_fsm by signal
        'prepared'
        '''
        dispatcher.send_minimal(sender=self.plc,
                                signal='prepared')
        
        self.assertEquals([()], self.mock.prepared.call_args_list)

    def test_7_connection_by_not_prepared(self):
        '''
        test connection between plc and kiosk_fsm by signal
        'not_prepared'
        '''
        dispatcher.send_minimal(sender=self.plc,
                                signal='not_prepared')
        
        self.assertEquals([()], self.mock.not_prepared.call_args_list)

    def test_8_connection_by_dispense_amount_changed(self):
        '''
        test connection between cash_fsm and kiosk_fsm by signal
        'dispense_amount_changed'
        '''
        dispatcher.send_minimal(sender=self.cash_fsm,
                                signal='dispense_amount_changed',
                                amount=10)
        
        self.assertEquals([({'amount':10,},)],
                          self.mock._dispense_amount_changed.call_args_list)

    def test_9_connection_by_deposit_amount_changed(self):
        '''
        test connection between cash_fsm and kiosk_fsm by signal
        'deposit_amount_changed'
        '''
        dispatcher.send_minimal(sender=self.cash_fsm,
                                signal='deposit_amount_changed',
                                amount=10)
        
        self.assertEquals([({'amount':10,},)],
                          self.mock._deposit_amount_changed.call_args_list)

    def test_10_connection_by_total_amount_changed(self):
        '''
        test connection between cash_fsm and kiosk_fsm by signal
        'total_amount_changed'
        '''
        dispatcher.send_minimal(sender=self.cash_fsm,
                                signal='total_amount_changed',
                                amount=10)
        
        self.assertEquals([({'amount':10,},)],
                          self.mock._total_amount_changed.call_args_list)

    def test_11_connection_by_coin_amount_changed(self):
        '''
        test connection between cash_fsm and kiosk_fsm by signal
        'coin_amount_changed'
        '''
        dispatcher.send_minimal(sender=self.cash_fsm,
                                signal='coin_amount_changed',
                                amount=10)
        
        self.assertEquals([({'amount':10,},)],
                          self.mock._coin_amount_changed.call_args_list)

    def test_12_connection_by_bill_amount_changed(self):
        '''
        test connection between cash_fsm and kiosk_fsm by signal
        'bill_amount_changed'
        '''
        dispatcher.send_minimal(sender=self.cash_fsm,
                                signal='bill_amount_changed',
                                amount=10)
        
        self.assertEquals([({'amount':10,},)],
                          self.mock._bill_amount_changed.call_args_list)

    def test_13_connection_by_bill_count_changed(self):
        '''
        test connection between cash_fsm and kiosk_fsm by signal
        'bill_count_changed'
        '''
        dispatcher.send_minimal(sender=self.cash_fsm,
                                signal='bill_count_changed',
                                count=10)
        
        self.assertEquals([({'count':10,},)],
                          self.mock._bill_count_changed.call_args_list)

    def test_14_connection_by_coin_in(self):
        '''
        test connection between cash_fsm and kiosk_fsm by signal
        'coin_in'
        '''
        dispatcher.send_minimal(sender=self.cash_fsm,
                                signal='coin_in',
                                amount=10)
        
        self.assertEquals([({'amount':10,},)],
                          self.mock._coin_in.call_args_list)

    def test_15_connection_by_bill_in(self):
        '''
        test connection between cash_fsm and kiosk_fsm by signal
        'bill_in'
        '''
        dispatcher.send_minimal(sender=self.cash_fsm,
                                signal='bill_in',
                                amount=10)
        
        self.assertEquals([({'amount':10,},)],
                          self.mock._bill_in.call_args_list)


class KioskFSMStub(KioskFSM):
    
    def __init__(self, plc, cash_fsm, products):
        self.mock = MagicMock()
        self.mock._connect_input_signals = MagicMock(
                                             spec="_connect_input_signals")
        super(KioskFSMStub, self).__init__(plc, cash_fsm, products)
        
    def _connect_input_signals(self, cash_fsm, plc, receiver):
        self.mock._connect_input_signals(cash_fsm=cash_fsm,
                                         plc=plc,
                                         receiver=receiver)
        
    