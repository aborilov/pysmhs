'''
Action Handler
'''
from abstracthandler import AbstractHandler


class actionhandler(AbstractHandler):

    def __init__(self, parent=None, params={}):
        AbstractHandler.__init__(self, parent, params)
        self.actions = {"setter": self.setter, "switcher": self.switcher}
        self.actionlist = {}
        for name, params in self.config.items():
            for tag, value in params["conditions"].items():
                self.actionlist.setdefault(tag, {})[value] = params["actions"]
        self.logger.debug(self.actionlist)

    def process(self, signal, events):
        self.logger.debug(events)
        for event in events:
            tag, value = event.values()
            if tag in self.actionlist and value in self.actionlist[tag]:
                for action, params in self.actionlist[tag][value].items():
                    self.actions.get(action, None)(params)

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
