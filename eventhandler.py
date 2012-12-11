'''
Created on Jan 24, 2012

@author: pavel
'''

from pydispatch import dispatcher
import threading


class EventHandler(object):
    '''
        Abstract class for all EventHandler
        You only need to implement method proccess(self,signal,events,polling)
        You can use self.params to get parameters for your action
    '''

    def __init__(self, params, polling):
        dispatcher.connect(self.handler, signal=params.setdefault(
            "signals", dispatcher.Any))
        self.params = params
        self.polling = polling

    def handler(self, signal, events):
        '''
        method accept events from dispacher
        @param signal:
        @param events:
        '''
        t1 = threading.Thread(target=self.proccess, args=(signal, events))
        t1.start()

    def proccess(self, signal, events):
        '''
        Method need to be implemented
        accept events, with list of changed tags
        and polling object, that have methods getTag and setTag
        '''
        raise NameError("Method not implemented by derived class")

    def stop(self):
        '''
        Method need to be implemented
        In this method handler have to close all resource
        and stop all threads
        '''
        print "stop EventHandler " + str(self)
