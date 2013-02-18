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

    port = None

    def __init__(self, parent=None, params={}):
        self.params = params
        AbstractHandler.__init__(self, parent, params)
        self.logger.info("Init web handler")
        resource = File(params["wwwPath"])
        root = Resource()
        root.putChild("www", resource)
        root.putChild("get", smhs_web(parent))
        self.site = server.Site(root)

    def loadtags(self):
        pass

    def run(self):
        AbstractHandler.run(self)
        self.port = reactor.listenTCP(int(self.params["port"]), self.site)

    def stop(self):
        AbstractHandler.stop(self)
        if self.port:
            self.port.stopListening()


class smhs_web(resource.Resource):
    isLeaf = True
    action_get_json = "getJson"
    actionStopServer = "stopServer"
    action_list_tags = "listTags"
    action_set_tag = "setTag"

    def __init__(self, parent):
        self.parent = parent
        resource.Resource.__init__(self)

    def render_GET(self, request):
        if ("action" in request.args):
            if (request.args["action"][0] == self.action_get_json):
                html = "{ \"tags\":{"
                coils = self.parent.tags
                for x in coils:
                    html += "\"" + x + "\":\"" + str(coils[x]) + "\","
                html += "} }"
                return html
            elif (request.args["action"][0] == self.action_list_tags):
                tags = self.parent.tags
                html = ''
                html += '<table>'
                for tag in sorted(tags):
                    html += '<tr>'
                    html += '<td>%s</td><td>%s</td>' % (tag, tags[tag])
                    html += '</tr>'
                return html
            elif (request.args["action"][0] == self.action_set_tag):
                l = request.args
                del l['action']
                html = ''
                for tag in l:
                    self.parent.settag(tag, int(l[tag][0]))
                    html += "setting %s to %s" % (tag, l[tag][0])
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
