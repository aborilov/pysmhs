'''
Core handler
'''
from abstracthandler import AbstractHandler


class corehandler(AbstractHandler):
    '''
    CoreHandler
    '''

    def __init__(self, parent=None, params={}):
        assert "configfile" in params, "no param configfile"
        self.listeners = {}
        AbstractHandler.__init__(self, parent, params)
        params = self.config[__name__]["params"]
        self.logger.info('Init core server')
        if self.config[__name__].get("run", "1") == "1":
            self.start()

    def loadtags(self):
        for tag in self.config:
            self._settag(tag, 0)

    def _addhandler(self, classname, parent, params):
        if not classname in self.listeners:
            try:
                _temp = __import__(
                    classname, globals(), locals(), [classname])
                handler = eval(
                    "_temp." + classname + "(parent, params)")
                self.listeners[classname] = handler
            except ImportError, e:
                print e

    def _addhandlers(self, handlers):
        for tag in handlers:
            if tag != __name__:
                try:
                    classname = tag
                    params = handlers[tag].get("params", {})
                    parentname = handlers[tag].get("parent")
                    if parentname == __name__:
                        parent = self
                    else:
                        parent = self.listeners.get(parentname, None)
                    self._addhandler(classname, parent, params)
                    if handlers[tag].get("run", "1") == "1":
                        self.listeners[classname].start()
                except KeyError, e:
                    print "No such param " + str(e)

    def runhandler(self, classname):
        if classname in self.listeners:
            self.listeners[classname].start()

    def _settag(self, tag, value):
        self.logger.debug("Setting tag %s to %s" % (tag, value))
        l = tag.split("_")
        if len(l) == 2:
            if l[0] == __name__:
                self._tags[l[1]] = value
            else:
                self.listeners[l[0]].settag(l[1], value)
        else:
            self._tags[tag] = value

    def _gettag(self, tag):
        l = tag.split("_")
        if len(l) == 2:
            if l[0] == __name__:
                return self._tags[l[1]]
            else:
                return self.listeners[l[0]].gettag(l[1])
        else:
            return self._tags[tag]

    @property
    def tags(self):
        tagslist = {}
        for listener in self.listeners.values():
            for tag in listener.tags:
                tagslist[
                    "%s_%s" %
                    (listener.__class__.__name__, tag)] = listener.tags[tag]
        for tag in self._tags:
            tagslist["%s_%s" % (__name__, tag)] = self._tags[tag]
        return tagslist

    def stop(self):
        for listener in self.listeners.values():
            if listener.isAlive():
                listener.stop()

    def run(self):
        self.logger.debug("RUN")
        self._settag(__name__, 1)
        self._addhandlers(self.config)
        while any(l.isAlive() for l in self.listeners.values()):
            for l in self.listeners.values():
                if l.isAlive():
                    l.join(1)
                    break
