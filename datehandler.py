'''
Date handler
'''
from abstracthandler import AbstractHandler
from datetime import datetime


class datehandler(AbstractHandler):

    def _gettag(self, tag):
        if tag == "date":
            return datetime.now()

    def updatedate(self):
        self._settag("date", datetime.now().strftime("%d.%m.%Y %H:%M:%S"))

    def loadtags(self):
        AbstractHandler.loadtags(self)
        self.updatedate()

    @property
    def tags(self):
        self.updatedate()
        return self._tags
