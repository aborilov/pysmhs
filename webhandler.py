'''
Web server handler
'''
from abstracthandler import AbstractHandler
from twisted.web import server, resource
from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web.static import File
import cgi


class webhandler(AbstractHandler):
    '''Web server handler'''

    def __init__(self, parent=None, params={}):
        AbstractHandler.__init__(self, parent, params)
        self.logger.info("Init web handler")
        resource = File(params["wwwPath"])
        root = Resource()
        root.putChild("www", resource)
        root.putChild("get", Simple(parent))
        site = server.Site(root)
        reactor.listenTCP(int(params["port"]), site)

    def loadtags(self):
        pass

    def run(self):
        AbstractHandler.run(self)
        reactor.run(installSignalHandlers=0)

    def stop(self):
        AbstractHandler.stop(self)
        reactor.stop()


class Simple(resource.Resource):
    isLeaf = True
    actionGetJson = "getJson"
    actionStopServer = "stopServer"

    def __init__(self, parent):
        self.parent = parent
        resource.Resource.__init__(self)

    def render_GET(self, request):
        if ("action" in request.args):
            if (request.args["action"][0] == self.actionGetJson):
                html = "{ \"tags\":{"
                coils = self.parent.tags
                for x in coils:
                    html += "\"" + x + "\":\"" + str(coils[x]) + "\","
                html += "} }"
                return html
            else:
                if (request.args["action"][0] == self.actionStopServer):
                    self.parent.stop()
                    return "Close"
        return "unknown url"

    def render_POST(self, request):
        for x in request.args:
            if (cgi.escape(request.args[x][0]) == "1"):
                self.parent.settag(x, 1)
            else:
                self.parent.settag(x, 0)
