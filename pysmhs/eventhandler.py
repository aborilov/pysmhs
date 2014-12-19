class EventHandler(object):
    '''
        Abstract class for all EventHandler
        You only need to implement method proccess(self,signal,events,polling)
        You can use self.params to get parameters for your action
    '''

    def __init__(self, params, polling):
        self.params = params
        self.polling = polling

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
        '''
        print "stop EventHandler " + str(self)
