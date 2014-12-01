'''
Action Handler
'''
from abstracthandler import AbstractHandler
import time
import logging

logger = logging.getLogger()


class actionhandler(AbstractHandler):

    def __init__(self, parent=None, params={}):
        AbstractHandler.__init__(self, parent, params)
        self.actions = {'setter': self.setter,
                        'switcher': self.switcher,
                        'sleep': self.sleep}
        self.temp_tags = {}

    def process(self, signal, events):
        for event in events:
            logger.debug(event)
            self.temp_tags[event['tag']] = event['value']
            for tag, params in self.config.items():
                if 'condition' in params:
                    params = params.copy()
                    cond = params.pop('condition')
                    if event['tag'] in cond:
                        logger.debug("check cond %s" % cond)
                        try:
                            logger.debug("eval %s" % eval(cond))
                            if eval(cond):
                                self._settag(tag, '1')
                        except Exception, e:
                            logger.error(
                                "Error(%s) while eval(%s)" % (e, cond))
        self.temp_tags = {}
        logger.debug('End of process')

    def gettag(self, tag):
        if tag in self.temp_tags:
            return int(self.temp_tags[tag])
        return AbstractHandler.gettag(self, tag)

    def _settag(self, tag, value):
        AbstractHandler._settag(self, tag, value)
        if str(value) == '1':
            self.run_action(tag)

    def run_action(self, tag):
        params = self.config[tag].copy()
        logger.debug('have actions %s' % sorted(params))
        if 'condition' in params:
            params.pop('condition')
        for i in sorted(params):
            logger.debug('Now in %s' % i)
            l = i.split(".")
            if len(l) == 2:
                action = l[1]
                param = params[i]
                logger.debug('Call method %s' % i)
                self.actions.get(action, None)(param)
            else:
                logger.debug(
                    'Wrong action name and order - %s' % i)
        logger.debug('have after actions %s' % sorted(params))
        self._settag(tag, '0')

    def loadtags(self):
        for tag in self.config:
            self._tags[tag] = '0'

    def switcher(self, params):
        for tag in params:
            self._inverttag(tag)

    def setter(self, params):
        for tag, value in params.items():
            self.settag(tag, value)

    def _inverttag(self, tag):
        if str(self.gettag(tag)) == '0':
            self.settag(tag, '1')
        else:
            self.settag(tag, '0')

    def sleep(self, params):
        logger.debug('before timeout')
        time.sleep(float(params.get('timeout', 1)))
        logger.debug('after timeout')
