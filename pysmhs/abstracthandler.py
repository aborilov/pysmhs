import louie
from louie import dispatcher, TwistedDispatchPlugin
from config.configobj import ConfigObj
from datetime import datetime

louie.install_plugin(TwistedDispatchPlugin)

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

logger = logging.getLogger('abstracthandler')

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

    def sendevents(self, tag, value):
        '''
        send event
        '''
        logger.debug(
            'Send tag: {} with value {} from {}'.format(
                tag, value, self.signal))
        dispatcher.send(signal=self.signal, event={tag:value})

    def settag(self, tag, value):
        '''
        Private method for settag
        set tag to value in tags
        Override if you need some action
        '''
        if self._tags[tag] != value:
            logger.debug('change tag {} to value {}'.format(tag, value))
            self._tags[tag] = value
            self.sendevents(tag, value)

    def gettag(self, tag):
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
            "listensignals", dispatcher.Any))
