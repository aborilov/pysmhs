'''
Date handler
'''
from abstracthandler import AbstractHandler
from datetime import datetime, time
from twisted.internet.task import LoopingCall
from dateutil.parser import parse
from dateutil.rrule import *
import urllib2
from xml.dom import minidom


class datehandler(AbstractHandler):

    midnight = time(00, 00, 00)

    def updatedate(self):
        now = datetime.now()
        self._tags['date'] = now.strftime("%d.%m.%Y %H:%M:%S")
        self.checktags(now)
        if now.time().replace(microsecond=0) == self.midnight:
            self._tags['sunset'] = self.getsunset().strftime("%H:%M:%S")
            self._tags['sunrise'] = self.getsunrise().strftime("%H:%M:%S")    

    def loadtags(self):
        self._tags['sunset'] = self.getsunset().strftime("%H:%M:%S")
        self._tags['sunrise'] = self.getsunrise().strftime("%H:%M:%S")
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

    def earthtool(self, param):
        now = datetime.now()
        xml = urllib2.urlopen(
            "http://www.earthtools.org/sun/54.32/36.16/" + str(now.day) + "/" + str(now.month) + "/+4/0").read()
        xmldoc = minidom.parseString(xml)
        itemlist = xmldoc.getElementsByTagName(param) 
        return parse(itemlist[0].childNodes[0].nodeValue).time()

    def getsunset(self):
        sunset = time(hour=20, minute=00, second=0, microsecond=0)
        try:
            sunset = self.earthtool('sunset')
        except Exception as inst:
            self.logger.error("Cant get sunset")
            print("error" + str(inst))
        return sunset

    def getsunrise(self):
        sunrise = time(hour=8, minute=00, second=0, microsecond=0)
        try:
            sunrise = self.earthtool('sunrise')
        except Exception as inst:
            self.logger.error("Cant get sunrise")
            print("error" + str(inst))
        return sunrise

    def checktag(self, tag, dt):
        dt = dt.replace(second=0, microsecond=0)
        if dt in self.rrules[tag]["startrr"]:
            self._settag(tag, '1')
        elif dt in self.rrules[tag]["endrr"]:
            self._settag(tag, '0')

    def checktags(self, dt):
        for tag in self.rrules:
            self.checktag(tag, dt)

    def start(self):
        AbstractHandler.start(self)
        self.lc = LoopingCall(self.updatedate)
        self.lc.start(1)

    def stop(self):
        AbstractHandler.stop(self)
        if self.lc:
            self.lc.stop()
