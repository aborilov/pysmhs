'''
Action Handler
'''
from abstracthandler import AbstractHandler


class newactionhandler(AbstractHandler):

    def __init__(self, parent=None, params={}):
        AbstractHandler.__init__(self, parent, params)
        self.actions = {'setter': self.setter, 'switcher': self.switcher}
        self.actionlist = {}
        for name, params in self.config.items():
            self.actionlist[params['condition']] = params['actions']

    def process(self, signal, events):
        #fix dont ask for tag value that in events
        self.logger.debug(events)
        for event in events:
            tag, value = event.values()
            for cond in [x for x in self.actionlist.keys() if tag in x]:
                self.logger.debug(eval(cond))
                try:
                    if eval(cond):
                        for i in sorted(self.actionlist[cond]):
                            action = self.actionlist[cond][i].pop('action')
                            params = self.actionlist[cond][i]
                            self.actions.get(action, None)(params)
                except:
                    self.logger.error("Error while eval condition - %s" % cond)

    def loadtags(self):
        for tag in self.config:
            self._tags[tag] = 0

    def switcher(self, params):
        for tag in params:
            self._inverttag(tag)

    def setter(self, params):
        for tag, value in params.items():
            self.settag(tag, value)

    def _inverttag(self, tag):
        if self.gettag(tag) == 0:
            self.settag(tag, 1)
        else:
            self.settag(tag, 0)
