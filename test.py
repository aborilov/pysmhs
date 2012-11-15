from twisted.application import service
from twisted.words.protocols.jabber import jid
from wokkel.client import XMPPClient
from twisted.internet import reactor
from twisted.words.xish import domish
from wokkel.xmppim import MessageProtocol, AvailablePresence
from twisted.python import log
import sys

class EchoBotProtocol(MessageProtocol):
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
            if str(msg.body) == "getStatus":
                rv = "this status"
                
            reply.addElement("body", content=rv)
            self.send(reply)


log.startLogging(sys.stdout, setStdout=0)
xmppclient = XMPPClient(jid.internJID("naxho@jabber.org/echobot"), "svan12")
xmppclient.logTraffic = True
echobot = EchoBotProtocol()
echobot.setHandlerParent(xmppclient)
xmppclient.startService()
reactor.run(installSignalHandlers=0)