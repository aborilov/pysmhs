'''
Action Handler
'''
from abstracthandler import AbstractHandler
import time


class actionhandler(AbstractHandler):

    def __init__(self, parent=None, params={}):
        AbstractHandler.__init__(self, parent, params)
        self.actions = {'setter': self.setter, 'switcher': self.switcher, 'sleep': self.sleep}
        self.actionlist = {}
        self.temp_tags = {}
        for name, params in self.config.items():
            cond = params.pop('condition')
            self.actionlist[cond] = params

    def process(self, signal, events):
        for event in events:
            self.logger.debug(event)
            self.temp_tags[event['tag']] = event['value']
            for cond in self.actionlist.keys():
                if event['tag'] in cond:
                    self.logger.debug("check cond %s" % cond)
                    try:
                        self.logger.debug("eval %s" % eval(cond))
                        if eval(cond):
                            self.logger.debug('have actions %s' % sorted(self.actionlist[cond]))
                            for i in sorted(self.actionlist[cond]):
                                self.logger.debug('Now in %s' % i)
                                l = i.split(".")
                                if len(l) == 2:
                                    action = l[1]
                                    params = self.actionlist[cond][i]
                                    self.logger.debug('Call method %s' % i)
                                    self.actions.get(action, None)(params)
                                else:
                                    self.logger.debug('Wrong action name and order - %s' % i)
                                self.logger.debug('have after actions %s' % sorted(self.actionlist[cond]))
                    except Exception, e:
                        self.logger.error("Error(%s) while eval(%s)" % (e, cond))
        self.temp_tags = {}
        self.logger.debug('End of process')

    def gettag(self, tag):
        if tag in self.temp_tags:
            return int(self.temp_tags[tag])
        return AbstractHandler.gettag(self, tag)

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
        if self.gettag(tag) == '0':
            self.settag(tag, '1')
        else:
            self.settag(tag, '0')

    def sleep(self, params):
        self.logger.debug('before timeout')
        time.sleep(float(params.get('timeout', 1)))
        self.logger.debug('after timeout')
