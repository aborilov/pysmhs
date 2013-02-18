'''
Created on Jul 17, 2012

@author: pavel
'''
from pydispatch import dispatcher
import threading
import logging
import threading
import logging.handlers
from config.configobj import ConfigObj


class AbstractHandler(threading.Thread):
    '''
    Abstractss class for all
    handlers
    '''

    def __init__(self, parent=None, params={}):
        threading.Thread.__init__(self)
        if "configfile" in params:
            self.config = ConfigObj(
                params["configfile"], indent_type="\t")
        self.signal = self.__class__.__name__
        self.params = params
        self.parent = parent
        self._tags = {}
        self.events = []
        loglevel = params.get('loglevel', 'debug').upper()
        filename = params.get('logfile', 'smhs.log')
        logfiles_num = int(params.get('logfiles_num', 5))
        logfile_size = int(params.get('logfile_size', 1048576))
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(getattr(logging, loglevel))
        handler = logging.handlers.RotatingFileHandler(
            filename, maxBytes=logfile_size, backupCount=logfiles_num)
        form = logging.Formatter(
            '%(asctime)s %(name)-12s %(levelname)s:%(message)s')
        handler.setFormatter(form)
        self.logger.addHandler(handler)
        self.logger.debug("Have params - " + str(self.params))
        self.logger.debug("Have parent - " + str(self.parent))
        self.loadtags()

    def __handler(self, signal, events):
        '''
        method accept events from dispacher
        @param signal:
        @param events:
        '''
        t1 = threading.Thread(target=self.process, args=(signal, events))
        t1.start()

    def process(self, signal, events):
        '''
        Method need to be implemented
        accept events, with list of changed tags
        '''
        pass

    def sendevents(self):
        '''
        send all events
        '''
        if self.events:
            for event in self.events:
                event["tag"] =\
                    "%s_%s" % (self.__class__.__name__, event["tag"])
                event["value"] = str(event["value"])
            dispatcher.send(signal=self.signal, events=self.events)
            self.events = []

    def settag(self, tag, value):
        '''
        set tag to value
        if parent call his method
        else call private method
        '''
        if self.parent:
            l = tag.split("_")
            if len(l) == 2:
                if l == self.__class__.__name__:
                    self._settag(l[1], value)
                else:
                    self.parent.settag(tag, value)
            else:
                self.logger.error("Can't parse handler name from tag " + tag)
        else:
            self._settag(tag, value)

    def _settag(self, tag, value):
        '''
        Private method for settag
        set tag to value in tags
        Override if you need some action
        '''
        self._tags[tag] = value

    def gettag(self, tag):
        '''
        get tag value
        if parent call his method
        else call private method

        '''
        self.logger.info("gettag " + tag)
        if self.parent:
            l = tag.split("_")
            if len(l) == 2:
                if l[0] == __name__:
                    return self._gettag(l[1])
                else:
                    return self.parent.gettag(tag)
            else:
                self.logger.error("Can't parse handler name from tag " + tag)
        else:
            return self._gettag(tag)

    def _gettag(self, tag):
        '''
        Private method for gettag
        get tag from tags
        Override if you need some action
        '''
        self.logger.debug("RETURN %s" % self._tags[tag])
        return self._tags[tag]

    @property
    def tags(self):
        return self._tags

    def loadtags(self):
        '''
        Load tags from config
        '''
        pass

    def stop(self):
        '''
        Stop handler
        '''
        self.logger.info("Stop handler")
        dispatcher.disconnect(self.handler, signal=self.params.get(
            "listensignals", dispatcher.Any))

    def start(self):
        '''
        Start handler
        '''
        self.logger.info("Start handler")
        dispatcher.connect(self.handler, signal=self.params.get(
            "signals", dispatcher.Any))
        threading.Thread.start(self)

    def run(self):
        threading.Thread.run(self)
