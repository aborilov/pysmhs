from pydispatch import dispatcher
from config.configobj import ConfigObj
from datetime import datetime

import logging
import logging.handlers

logfiles_num = 5
logfile_size = 1048576
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(
    'smhs.log', maxBytes=logfile_size, backupCount=logfiles_num)
form = logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)s:%(message)s')
handler.setFormatter(form)
logger.addHandler(handler)

class AbstractHandler(object):

    '''
    Abstractss class for all handlers
    '''

    def __init__(self, parent=None, params={}):
        if "configfile" in params:
            self.config = ConfigObj(params["configfile"], indent_type="\t")
        self.signal = self.__class__.__name__
        self.params = params
        self.stopped = True
        self.parent = parent
        self._tags = {}
        self.events = []
        logger.debug("Have params - " + str(self.params))
        logger.debug("Have parent - " + str(self.parent))
        self.loadtags()

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
                event["date"] = datetime.now()
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
        logger.info("settag " + tag)
        if self.parent:
            l = tag.split("_")
            if len(l) == 2:
                if l == self.__class__.__name__:
                    self._settag(l[1], value)
                else:
                    try:
                        self.parent.settag(tag, value)
                    except:
                        logger.error(
                            "Can't set tag %s with value %s" % (
                                tag, value),
                            exc_info=1)
            else:
                self._settag(tag, value)
        else:
            self._settag(tag, value)

    def _settag(self, tag, value):
        '''
        Private method for settag
        set tag to value in tags
        Override if you need some action
        '''
        if self._tags[tag] != value:
            self._tags[tag] = value
            self.events.append({"tag": tag, "value": value})
            self.sendevents()

    def gettag(self, tag):
        '''
        get tag value
        if parent call his method
        else call private method

        '''
        logger.info("gettag " + tag)
        if self.parent:
            l = tag.split("_")
            if len(l) == 2:
                if l[0] == __name__:
                    return self._gettag(l[1])
                else:
                    return self.parent.gettag(tag)
            else:
                return self._gettag(tag)
        else:
            return self._gettag(tag)

    def _gettag(self, tag):
        '''
        Private method for gettag
        get tag from tags
        Override if you need some action
        '''
        logger.debug("RETURN %s" % self._tags[tag])
        return self._tags[tag]

    @property
    def tags(self):
        if self.stopped:
            return {}
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
        self.stopped = True
        logger.info("Stop handler")
        dispatcher.disconnect(self.process, signal=self.params.get(
            "listensignals", dispatcher.Any))

    def start(self):
        '''
        Start handler
        '''
        self.stopped = False
        logger.info("Start handler")
        dispatcher.connect(self.process, signal=self.params.get(
            "signals", dispatcher.Any))
