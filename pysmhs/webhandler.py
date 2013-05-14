# -*- coding: utf-8 -*-
'''
Web server handler
'''
from abstracthandler import AbstractHandler
from twisted.web import server, resource
from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web.static import File
import collections
import cgi
from jinja2 import Environment, PackageLoader


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

    def start(self):
        AbstractHandler.start(self)
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
        env = Environment(loader=PackageLoader('www', 'templates'))
        self.listtags_template = env.get_template('listtags_template.html')
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
                od = {}
                handler = ""
                for tag in sorted(tags):
                    if tag.split('_')[0] != handler:
                        handler = tag.split('_')[0]
                    od.setdefault(handler, {})[tag.split('_')[1]] = str(tags[tag])
                return str(self.listtags_template.render(title=u'Tag list',
                                                         description='here',
                                                         tags=od))
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
