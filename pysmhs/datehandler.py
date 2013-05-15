'''
Date handler
'''
from abstracthandler import AbstractHandler
from datetime import datetime
from twisted.internet.task import LoopingCall


class datehandler(AbstractHandler):

    def _gettag(self, tag):
        if tag == "date":
            return datetime.now()
        return AbstractHandler._gettag(self, tag)

    def updatedate(self):
        self._tags['date'] = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    def loadtags(self):
        for tag in self.config:
            self.settag(tag, '0')
        # self.updatedate()

    # @property
    # def tags(self):
    #     if self.stopped:
    #         return {}
    #     # self.updatedate()
    #     print self._tags
    #     return self._tags

    def start(self):
        AbstractHandler.start(self)
        self.lc = LoopingCall(self.updatedate)
        self.lc.start(1)

    def stop(self):
        AbstractHandler.stop(self)
        if self.lc:
            self.lc.stop()
