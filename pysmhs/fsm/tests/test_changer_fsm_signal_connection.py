from louie import dispatcher

from unittest import TestCase

from pysmhs.fsm.changer_fsm import ChangerFSM


try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock
    

class TestChangerFsm(TestCase):
    
    def setUp(self):
        self.changer = MagicMock()

        self.mock = MagicMock()
        self.mock.online = MagicMock(spec="online")
        self.mock.offline = MagicMock(spec="offline")
        self.mock.initialized = MagicMock(spec="initialized")
        self.mock.error = MagicMock(spec="error")
        self.mock._on_coin_in = MagicMock(spec="_on_coin_in")
        self.mock._on_coin_out = MagicMock(spec="_on_coin_out")
        
        self.fsm = ChangerFSM(changer=self.changer)
        self.fsm._connect_input_signals(sender=self.changer,
                                                receiver=self.mock)
        
    def tearDown(self):
        pass

    def test_1_connect_receiver_to_sender(self):
        '''
        test that method _connect_receiver_to_sender is called on
        changer_fsm initialized
        '''
        changer_fsm_stub = ChangerFSMStub(changer=self.changer)
        
        self.assertEquals([({'sender':self.changer,
                             'receiver':changer_fsm_stub},)],
                  changer_fsm_stub.mock._connect_input_signals.call_args_list)

    def test_2_connection_by_online(self):
        '''
        test connection between changer and changer_fsm by signal 'online'
        '''
        dispatcher.send_minimal(sender=self.changer, signal='online')
        
        self.assertEquals([()], self.mock.online.call_args_list)

    def test_3_connection_by_offline(self):
        '''
        test connection between changer and changer_fsm by signal 'offline'
        '''
        dispatcher.send_minimal(sender=self.changer, signal='offline')
        
        self.assertEquals([()], self.mock.offline.call_args_list)

    def test_4_connection_by_initialized(self):
        '''
        test connection between changer and changer_fsm by signal 'initialized'
        '''
        dispatcher.send_minimal(sender=self.changer, signal='initialized')
        
        self.assertEquals([()], self.mock.initialized.call_args_list)

    def test_5_connection_by_error(self):
        '''
        test connection between changer and changer_fsm by signal 'error'
        '''
        dispatcher.send_minimal(sender=self.changer, signal='error',
                                error_code='code',
                                error_text='text')
        
        self.assertEquals([({'error_code':'code',
                             'error_text':'text',},)],
                          self.mock.error.call_args_list)

    def test_6_connection_by_coin_in(self):
        '''
        test connection between changer and changer_fsm by signal 'coin_in'
        '''
        dispatcher.send_minimal(
            sender=self.changer, signal='coin_in', amount=10)
        
        self.assertEquals([({'amount':10,},)],
                          self.mock._on_coin_in.call_args_list)

    def test_7_connection_by_coin_out(self):
        '''
        test connection between changer and changer_fsm by signal 'coin_out'
        '''
        dispatcher.send_minimal(
            sender=self.changer, signal='coin_out', amount=10)
        
        self.assertEquals([({'amount':10,},)],
                          self.mock._on_coin_out.call_args_list)

class ChangerFSMStub(ChangerFSM):
    
    def __init__(self, changer):
        self.mock = MagicMock()
        self.mock._connect_input_signals = MagicMock(
                                             spec="_connect_input_signals")
        super(ChangerFSMStub, self).__init__(changer=changer)
        
    def _connect_input_signals(self, sender, receiver):
        self.mock._connect_input_signals(sender=sender, receiver=receiver)
        
    