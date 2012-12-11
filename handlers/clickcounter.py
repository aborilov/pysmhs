'''
Created on Apr 16, 2012

@author: pavel
'''
import logging
from eventhandler import EventHandler
from datetime import datetime
from pydispatch import dispatcher
from config.configreader import ConfigReader


class ClassHandler(EventHandler):

    def __init__(self, params, polling):
        EventHandler.__init__(self, params, polling)
        self.clicks = {}
        self.inputtags = ConfigReader.tags_config.get_tags_by_type("inputc")

    def proccess(self, signal, events):
        for tag in events:
            if tag in self.inputtags:
                self.addclick(tag)
                if self.clicks[tag]["click"] == 2:
                    dispatcher.send(
                        signal="CLICKevents", events={tag: "click"})
                    logging.info(tag + "=" + "click")
                if self.clicks[tag]["click"] == 4:
                    dispatcher.send(
                        signal="CLICKevents", events={tag: "doubleclick"})
                    logging.info(tag + "=" + "dounbleclick")
                if self.clicks[tag]["click"] == 6:
                    dispatcher.send(
                        signal="CLICKevents", events={tag: "triplclick"})
                    logging.info(tag + "=" + "triplclick")

    def stop(self):
        pass

    def addclick(self, tag):
        t = datetime.now()
        if tag in self.clicks:
            ci = t - self.clicks[tag]["date"]
            if ci.seconds < int(self.params["clickinterval"]):
                self.clicks[tag]["click"] = self.clicks[tag]["click"] + 1
            else:
                self.clicks[tag]["click"] = 1
        else:
            self.clicks[tag] = {}
            self.clicks[tag]["click"] = 1
        self.clicks[tag]["date"] = t
