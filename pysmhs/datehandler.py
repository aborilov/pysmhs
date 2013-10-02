'''
Date handler
'''
from abstracthandler import AbstractHandler
from datetime import datetime
from twisted.internet.task import LoopingCall
from dateutil.parser import parse
from dateutil.rrule import *


class datehandler(AbstractHandler):

    def updatedate(self):
        self._tags['date'] = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        self.checktags()

    def loadtags(self):
        self.rrules = {}
        for tag, params in self.config.items():
            startdate = parse(params["start"])
            enddate = parse(params["end"])
            untildate = parse(params["until"])
            freq = eval(params['freq'])
            startrr = rrule(
                freq, dtstart=startdate, until=untildate, cache=True)
            endrr = rrule(freq, dtstart=enddate, until=untildate, cache=True)
            self.settag(tag, '0')
            tagrrule = self.rrules.setdefault(tag, {})
            tagrrule["startrr"] = startrr
            tagrrule["endrr"] = endrr

    def checktag(self, tag):
        now = datetime.now().replace(second=0, microsecond=0)
        if now in self.rrules[tag]["startrr"]:
            self._settag(tag, '1')
        elif now in self.rrules[tag]["endrr"]:
            self._settag(tag, '0')

    def checktags(self):
        for tag in self.rrules:
            self.checktag(tag)

    def start(self):
        AbstractHandler.start(self)
        self.lc = LoopingCall(self.updatedate)
        self.lc.start(1)

    def stop(self):
        AbstractHandler.stop(self)
        if self.lc:
            self.lc.stop()
