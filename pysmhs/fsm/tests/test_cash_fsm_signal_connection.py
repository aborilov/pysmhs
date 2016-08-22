from louie import dispatcher

from unittest import TestCase

from pysmhs.fsm.cash_fsm import CashFSM


try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock
    

class TestCashFsm(TestCase):
    
    def setUp(self):
        self.changer_fsm = MagicMock()
        self.validator_fsm = MagicMock()

        self.mock = MagicMock()
        self.mock._on_changer_offline = MagicMock(spec="_on_changer_offline")
        self.mock._on_changer_ready = MagicMock(spec="_on_changer_ready")
        self.mock._on_changer_error = MagicMock(spec="_on_changer_error")
        self.mock._on_coin_in = MagicMock(spec="_on_coin_in")
        self.mock.amount_dispensed = MagicMock(spec="amount_dispensed")
        self.mock._on_validator_offline = MagicMock(spec="_on_validator_offline")
        self.mock._on_validator_ready = MagicMock(spec="_on_validator_ready")
        self.mock._on_validator_error = MagicMock(spec="_on_validator_error")
        self.mock._on_bill_in = MagicMock(spec="_on_bill_in")
        self.mock.check_bill = MagicMock(spec="check_bill")
        self.mock._coin_amount_changed = MagicMock(spec="_coin_amount_changed")
        self.mock._bill_amount_changed = MagicMock(spec="_bill_amount_changed")
        self.mock._bill_count_changed = MagicMock(spec="_bill_count_changed")
        
        self.fsm = CashFSM(changer_fsm=self.changer_fsm,
                           validator_fsm=self.validator_fsm)
        self.fsm._connect_input_signals(changer_fsm=self.changer_fsm,
                                        validator_fsm=self.validator_fsm,
                                        receiver=self.mock)
        
    def tearDown(self):
        pass

    def test_1_connect_receiver_to_sender(self):
        '''
        test that method _connect_receiver_to_sender is called on
        cash_fsm initialized
        '''
        cash_fsm_stub = CashFSMStub(changer_fsm=self.changer_fsm,
                                    validator_fsm=self.validator_fsm)
        
        self.assertEquals([({'changer_fsm':self.changer_fsm,
                             'validator_fsm':self.validator_fsm,
                             'receiver':cash_fsm_stub},)],
                  cash_fsm_stub.mock._connect_input_signals.call_args_list)

    def test_2_connection_by_changer_offline(self):
        '''
        test connection between changer_fsm and cash_fsm by
        signal 'offline'
        '''
        dispatcher.send_minimal(sender=self.changer_fsm, signal='offline')
        
        self.assertEquals([()], self.mock._on_changer_offline.call_args_list)

    def test_3_connection_by_changer_initialized(self):
        '''
        test connection between changer_fsm and cash_fsm by
        signal 'initialized'
        '''
        dispatcher.send_minimal(sender=self.changer_fsm, signal='initialized')
        
        self.assertEquals([()], self.mock._on_changer_ready.call_args_list)

    def test_4_connection_by_changer_error(self):
        '''
        test connection between changer_fsm and cash_fsm by signal 'error'
        '''
        dispatcher.send_minimal(sender=self.changer_fsm, signal='error',
                                error_code='code',
                                error_text='text')
        
        self.assertEquals([({'error_code':'code',
                             'error_text':'text',},)],
                          self.mock._on_changer_error.call_args_list)

    def test_5_connection_by_coin_in(self):
        '''
        test connection between changer_fsm and cash_fsm by signal 'coin_in'
        '''
        dispatcher.send_minimal(
            sender=self.changer_fsm, signal='coin_in', amount=10)
        
        self.assertEquals([({'amount':10,},)],
                          self.mock._on_coin_in.call_args_list)

    def test_6_connection_by_amount_dispensed(self):
        '''
        test connection between changer_fsm and cash_fsm by signal
        'amount_dispensed'
        '''
        dispatcher.send_minimal(
            sender=self.changer_fsm, signal='amount_dispensed', amount=10)
        
        self.assertEquals([({'amount':10,},)],
                          self.mock.amount_dispensed.call_args_list)

    def test_7_connection_by_validator_offline(self):
        '''
        test connection between validator_fsm and cash_fsm by
        signal 'offline'
        '''
        dispatcher.send_minimal(sender=self.validator_fsm, signal='offline')
        
        self.assertEquals([()], self.mock._on_validator_offline.call_args_list)

    def test_8_connection_by_validator_initialized(self):
        '''
        test connection between validator_fsm and cash_fsm by
        signal 'initialized'
        '''
        dispatcher.send_minimal(sender=self.validator_fsm, signal='initialized')
        
        self.assertEquals([()], self.mock._on_validator_ready.call_args_list)

    def test_9_connection_by_validator_error(self):
        '''
        test connection between validator_fsm and cash_fsm by signal 'error'
        '''
        dispatcher.send_minimal(sender=self.validator_fsm, signal='error',
                                error_code='code',
                                error_text='text')
        
        self.assertEquals([({'error_code':'code',
                             'error_text':'text',},)],
                          self.mock._on_validator_error.call_args_list)

    def test_10_connection_by_bill_in(self):
        '''
        test connection between validator_fsm and cash_fsm by signal 'bill_in'
        '''
        dispatcher.send_minimal(
            sender=self.validator_fsm, signal='bill_in', amount=10)
        
        self.assertEquals([({'amount':10,},)],
                          self.mock._on_bill_in.call_args_list)

    def test_11_connection_by_check_bill(self):
        '''
        test connection between validator_fsm and cash_fsm by signal
        'check_bill'
        '''
        dispatcher.send_minimal(
            sender=self.validator_fsm, signal='check_bill', amount=10)
        
        self.assertEquals([({'amount':10,},)],
                          self.mock.check_bill.call_args_list)

    def test_12_connection_by_coin_amount_changed(self):
        '''
        test connection between changer_fsm and cash_fsm by signal
        'total_amount_changed'
        '''
        dispatcher.send_minimal(
            sender=self.changer_fsm, signal='total_amount_changed', amount=10)
        
        self.assertEquals([({'amount':10,},)],
                          self.mock._coin_amount_changed.call_args_list)

    def test_13_connection_by_bill_amount_changed(self):
        '''
        test connection between validator_fsm and cash_fsm by signal
        'total_amount_changed'
        '''
        dispatcher.send_minimal(
            sender=self.validator_fsm, signal='total_amount_changed', amount=10)
        
        self.assertEquals([({'amount':10,},)],
                          self.mock._bill_amount_changed.call_args_list)

    def test_14_connection_by_bill_count_changed(self):
        '''
        test connection between validator_fsm and cash_fsm by signal
        'bill_count_changed'
        '''
        dispatcher.send_minimal(
            sender=self.validator_fsm, signal='bill_count_changed', count=10)
        
        self.assertEquals([({'count':10,},)],
                          self.mock._bill_count_changed.call_args_list)

    def test_15_no_connection_by_changer_online(self):
        '''
        test that no connection between validator_fsm and cash_fsm by signal
        'online'
        '''
        dispatcher.send_minimal(
            sender=self.changer_fsm, signal='online')
        
        self.assertEquals([], self.mock.mock_calls)
        
    def test_16_no_connection_by_validator_online(self):
        '''
        test that no connection between validator_fsm and cash_fsm by signal
        'online'
        '''
        dispatcher.send_minimal(
            sender=self.validator_fsm, signal='online')
        
        self.assertEquals([], self.mock.mock_calls)


class CashFSMStub(CashFSM):
    
    def __init__(self, changer_fsm, validator_fsm):
        self.mock = MagicMock()
        self.mock._connect_input_signals = MagicMock(
                                             spec="_connect_input_signals")
        super(CashFSMStub, self).__init__(changer_fsm, validator_fsm)
        
    def _connect_input_signals(self, changer_fsm, validator_fsm, receiver):
        self.mock._connect_input_signals(changer_fsm=changer_fsm,
                                         validator_fsm=validator_fsm,
                                         receiver=receiver)
        
    