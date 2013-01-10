'''
Action Handler
'''
from abstracthandler import AbstractHandler


class newactionhandler(AbstractHandler):

    def __init__(self, parent=None, params={}):
        AbstractHandler.__init__(self, parent, params)
        self.actions = {'setter': self.setter, 'switcher': self.switcher}
        self.actionlist = {}
        self.temp_tags = {}
        for name, params in self.config.items():
            self.actionlist[params['condition']] = params['actions']

    def process(self, signal, events):
        for event in events:
            self.temp_tags[event['tag']] = event['value']
            for cond in self.actionlist.keys():
                if event['tag'] in cond:
                    try:
                        if eval(cond):
                            for i in sorted(self.actionlist[cond]):
                                action = self.actionlist[cond][i].pop('action')
                                params = self.actionlist[cond][i]
                                self.actions.get(action, None)(params)
                    except:
                        self.logger.error("Error while eval(%s)" % cond)
        self.temp_tags = {}

    def gettag(self, tag):
        if tag in self.temp_tags:
            return self.temp_tags[tag]
        return AbstractHandler.gettag(tag)

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
