from louie import dispatcher

from unittest import TestCase

from pysmhs.fsm.validator_fsm import BillValidatorFSM


try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock
    

class TestValidatorFsm(TestCase):
    
    def setUp(self):
        self.validator = MagicMock()

        self.mock = MagicMock()
        self.mock.online = MagicMock(spec="online")
        self.mock.offline = MagicMock(spec="offline")
        self.mock.initialized = MagicMock(spec="initialized")
        self.mock.error = MagicMock(spec="error")
        self.mock.check_bill = MagicMock(spec="check_bill")
        self.mock.bill_in = MagicMock(spec="bill_in")
        
        self.fsm = BillValidatorFSM(validator=self.validator)
        self.fsm._connect_input_signals(sender=self.validator,
                                        receiver=self.mock)
        
    def tearDown(self):
        pass

    def test_1_connect_receiver_to_sender(self):
        '''
        test that method _connect_receiver_to_sender is called on
        validator_fsm initialized
        '''
        validator_fsm_stub = BillValidatorFSMStub(validator=self.validator)
        
        self.assertEquals([({'sender':self.validator,
                             'receiver':validator_fsm_stub},)],
                  validator_fsm_stub.mock._connect_input_signals.call_args_list)

    def test_2_connection_by_online(self):
        '''
        test connection between validator and validator_fsm by signal 'online'
        '''
        dispatcher.send_minimal(sender=self.validator, signal='online')
        
        self.assertEquals([()], self.mock.online.call_args_list)

    def test_3_connection_by_offline(self):
        '''
        test connection between validator and validator_fsm by signal 'offline'
        '''
        dispatcher.send_minimal(sender=self.validator, signal='offline')
        
        self.assertEquals([()], self.mock.offline.call_args_list)

    def test_4_connection_by_initialized(self):
        '''
        test connection between validator and validator_fsm by signal
        'initialized'
        '''
        dispatcher.send_minimal(sender=self.validator, signal='initialized')
        
        self.assertEquals([()], self.mock.initialized.call_args_list)

    def test_5_connection_by_error(self):
        '''
        test connection between validator and validator_fsm by signal 'error'
        '''
        dispatcher.send_minimal(sender=self.validator, signal='error',
                                error_code='code',
                                error_text='text')
        
        self.assertEquals([({'error_code':'code',
                             'error_text':'text',},)],
                          self.mock.error.call_args_list)

    def test_6_connection_by_coin_in(self):
        '''
        test connection between validator and validator_fsm by signal
        'check_bill'
        '''
        dispatcher.send_minimal(
            sender=self.validator, signal='check_bill', amount=10)
        
        self.assertEquals([({'amount':10,},)],
                          self.mock.check_bill.call_args_list)

    def test_7_connection_by_coin_out(self):
        '''
        test connection between validator and validator_fsm by signal 'bill_in'
        '''
        dispatcher.send_minimal(
            sender=self.validator, signal='bill_in', amount=10)
        
        self.assertEquals([({'amount':10,},)],
                          self.mock.bill_in.call_args_list)

class BillValidatorFSMStub(BillValidatorFSM):
    
    def __init__(self, validator):
        self.mock = MagicMock()
        self.mock._connect_input_signals = MagicMock(
                                             spec="_connect_input_signals")
        super(BillValidatorFSMStub, self).__init__(validator=validator)
        
    def _connect_input_signals(self, sender, receiver):
        self.mock._connect_input_signals(sender=sender, receiver=receiver)
        
    