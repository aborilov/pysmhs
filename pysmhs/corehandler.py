'''
Core handler
'''
from abstracthandler import AbstractHandler
from twisted.internet import reactor

import logging

logger = logging.getLogger('corehandler')


class corehandler(AbstractHandler):
    '''
    CoreHandler
    '''

    def __init__(self, parent=None, params={}):
        assert "configfile" in params, "no param configfile"
        self.handlers = {}
        AbstractHandler.__init__(self, parent, params)
        params = self.config[type(self).__name__]["params"]
        logger.info('Init core server')
        # if self.config[__name__].get("run", "1") == "1":
        #     self.start()

    def loadtags(self):
        for tag in self.config:
            self.settag(tag, self.config[tag].get("run", "1"))

    def _addhandler(self, classname, parent, params):
        if not classname in self.handlers:
            # try:
            _temp = __import__(
                classname, globals(), locals(), [classname])
            handler = eval(
                "_temp." + classname + "(parent, params)")
            self.handlers[classname] = handler
            # except ImportError, e:
            #     print e

    def _addhandlers(self, handlers):
        for tag in handlers:
            if tag != type(self).__name__:
                # try:
                classname = tag
                params = handlers[tag].get("params", {})
                parentname = handlers[tag].get("parent")
                if parentname == type(self).__name__:
                    parent = self
                else:
                    parent = self.handlers.get(parentname, None)
                self._addhandler(classname, parent, params)
                # except KeyError, e:
                #     print "No such param " + str(e)

    def runhandler(self, classname):
        if classname in self.handlers:
            self.handlers[classname].start()

    # def settag(self, tag, value):
        # self._settag(tag, value)

    def settag(self, tag, value):
        logger.debug("Setting tag %s to %s" % (tag, value))
        l = tag.split("_")
        # try:
        if len(l) == 2:
            if l[0] == type(self).__name__:
                if self._tags[l[1]] != value:
                    self._set_listeners(l[1], value)
                    AbstractHandler.settag(self, l[1], value)
            else:
                self.handlers[l[0]].settag(l[1], value)
        else:
            self._tags[tag] = value
        # except:
        #     logger.error(
        #         "Can't settag", exc_info=1)

    def _set_listeners(self, tag, value):
        if tag in self.handlers:
            if value:
                self.handlers[tag].start()
            else:
                self.handlers[tag].stop()

    def gettag(self, tag):
        l = tag.split("_")
        if len(l) == 2:
            if l[0] == type(self).__name__:
                return self._tags[l[1]]
            else:
                return self.handlers[l[0]].gettag(l[1])
        else:
            return self._tags[tag]

    @property
    def tags(self):
        tagslist = {}
        for listener in self.handlers.values():
            for tag in listener.tags:
                tagslist[
                    "%s_%s" %
                    (listener.__class__.__name__, tag)] = listener.tags[tag]
        for tag in self._tags:
            tagslist["%s_%s" % (type(self).__name__, tag)] = self._tags[tag]
        return tagslist

    def stop(self):
        AbstractHandler.stop(self)
        #for listener in self.handlers:
            #self._set_listeners(listener, 0)
        reactor.stop()

    def start(self):
        # self.stopped = False
        logger.debug("RUN")
        self.settag(type(self).__name__, '1')
        self._addhandlers(self.config)
        for listener in self.handlers:
            if self._tags[listener] == '1':
                self.handlers[listener].start()
        reactor.run(installSignalHandlers=0)
