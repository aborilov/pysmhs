import louie
from louie import dispatcher, TwistedDispatchPlugin
from config.configobj import ConfigObj
from datetime import datetime

louie.install_plugin(TwistedDispatchPlugin())

import sys
from os import path
import logging
import logging.handlers

logfiles_num = 5
logfile_size = 1048576
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
#  handler = logging.handlers.RotatingFileHandler(
    #  'smhs.log', maxBytes=logfile_size, backupCount=logfiles_num)
handler = logging.StreamHandler(sys.stdout)
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
            config_path = path.join(
                sys.prefix, 'etc/pysmhs', params['configfile'])
            self.config = ConfigObj(config_path, indent_type="\t")
        self.signal = self.__class__.__name__
        self.params = params
        self.stopped = True
        self.parent = parent
        self._tags = {}
        self.events = []
        logger.debug("Have params - " + str(self.params))
        logger.debug("Have parent - " + str(self.parent))
        self.loadtags()

    def _process(self, signal, event):
        try:
            return self.process(signal, event)
        except Exception:
            logger.exception("Error while process")

    def process(self, signal, event):
        '''
        Method need to be implemented
        accept events, with list of changed tags
        '''
        pass

    def sendevent(self, tag, value):
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
            self.sendevent(tag, value)

    def gettag(self, tag):
        '''
        Private method for gettag
        get tag from tags
        Override if you need some action
        '''
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
        self._tags = dict(self.config)

    def stop(self):
        '''
        Stop handler
        '''
        self.stopped = True
        logger.info("Stop handler")
        signals = self.params.get('listensignals', (dispatcher.All,))
        for signal in signals:
            try:
                dispatcher.disconnect(self._process, signal=signal)
            except:
                logger.exception("Error while try to disconnect listener")

    def start(self):
        '''
        Start handler
        '''
        self.stopped = False
        logger.info("Start handler: {}".format(self.__class__.__name__))
        signals = self.params.get('listensignals', (dispatcher.All,))
        for signal in signals:
            logger.debug('{} start listen for {}'.format(
                self.__class__.__name__, signal))
            dispatcher.connect(self._process, signal=signal)
