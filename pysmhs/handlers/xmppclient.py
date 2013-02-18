'''
Created on Apr 17, 2012

@author: pavel
'''

from twisted.application import service
from twisted.words.protocols.jabber import jid
from wokkel.client import XMPPClient
from twisted.internet import reactor
from twisted.words.xish import domish
from wokkel.xmppim import MessageProtocol, AvailablePresence
from eventhandler import EventHandler
import threading


class EchoBotProtocol(MessageProtocol):

    def __init__(self, polling):
        MessageProtocol.__init__(self)
        self.polling = polling

    def connectionMade(self):
        print "Connected!"

        # send initial presence
        self.send(AvailablePresence())

    def connectionLost(self, reason):
        print "Disconnected!"

    def onMessage(self, msg):
        print str(msg)

        if msg["type"] == 'chat' and hasattr(msg, "body"):
            reply = domish.Element((None, "message"))
            reply["to"] = msg["from"]
            reply["from"] = msg["to"]
            reply["type"] = 'chat'
            rv = "I don't understand you"
            message = str(msg.body)
            msgstrip = message.rsplit(":")
            if len(msgstrip) > 1:
                if msgstrip[0].lower() == "gettag":
                    rv = self.polling.tags[msgstrip[1]]
                if msgstrip[0].lower() == "settag":
                    paramstrip = msgstrip[1].rsplit("=")
                    rv = "wrong params"
                    if len(paramstrip) > 1:
                        tag = paramstrip[0]
                        value = int(paramstrip[1])
                        self.polling.settag(tag, value)
                        rv = "Done"
            if str(msg.body).lower() == "gettags":
                rv = str(self.polling.tags)
            reply.addElement("body", content=rv)
            self.send(reply)


class ClassHandler(EventHandler):

    def __init__(self, params, polling):
        EventHandler.__init__(self, params, polling)
        xmppclient = XMPPClient(jid.internJID(
            params["login"] + "/echobot"), params["password"])
        xmppclient.logTraffic = True
        echobot = EchoBotProtocol(polling)
        echobot.setHandlerParent(xmppclient)
        xmppclient.startService()
        self.xmppclient = threading.Thread(target=self.runxmppclient)
        self.xmppclient.start()

    def runxmppclient(self):
        '''
        run xmppclient
        '''
        reactor.run(installSignalHandlers=0)

    def proccess(self, signal, events):
        pass

    def stop(self):
        print "Stop xmppserver"
        reactor.stop()
