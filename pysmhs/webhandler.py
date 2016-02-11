# -*- coding: utf-8 -*-
'''
Web server handler
'''
from abstracthandler import AbstractHandler
from twisted.web import server, resource
from twisted.internet import reactor, defer
from twisted.web.resource import Resource
from twisted.web.static import File
import cgi
import json
from jinja2 import Environment, PackageLoader
from collections import OrderedDict
from uuid import uuid4

import logging
from pkg_resources import resource_filename

logger = logging.getLogger('webhandler')


class webhandler(AbstractHandler):

    '''Web server handler'''

    port = None

    def __init__(self, parent=None, params={}):
        self.cachemax = 255
        self.eventcache = OrderedDict()
        self.params = params
        self.waiter = []
        super(webhandler, self).__init__(parent, params)
        logger.info("Init web handler")
        #  resource = File(params["wwwPath"])
        root = File(resource_filename('pysmhs', 'www'))
        #  root.putChild("www", resource)
        root.putChild("get", smhs_web(parent))
        root.putChild("api", ApiResource(parent, self.waiter, self.eventcache))
        #root.putChild("mon", monitor(self.eventcache))
        self.site = server.Site(root)

    def loadtags(self):
        pass

    def process(self, signal, event):
        if len(self.eventcache) == self.cachemax:
            self.eventcache.popitem(last=False)
        self.addevent(event)

    def addevent(self, event):
        token = uuid4().hex
        self.eventcache[token] = event
        while self.waiter:
            request = self.waiter.pop()
            request.write(json.dumps({token: event}))
            request.finish()

    def start(self):
        super(webhandler, self).start()
        self.port = reactor.listenTCP(int(self.params["port"]), self.site)

    def stop(self):
        super(webhandler, self).stop()
        if self.port:
            self.port.stopListening()


class ApiResource(resource.Resource):

    isLeaf = False

    def __init__(self, parent, waiter, events):
        resource.Resource.__init__(self)
        self.corehandler = parent
        self.events = events
        self.waiter = waiter

    def getChild(self, handler, request):
        if handler == 'handlers':
            return HandlersResource(self.corehandler)
        if handler == 'events':
            return EventsResource(self.waiter, self.events)
        return self

    def render_GET(self, request):
        return "API version 0.1"


class EventsResource(resource.Resource):

    isLeaf = True

    def __init__(self, waiter, events):
        resource.Resource.__init__(self)
        self.events = events
        self.waiter = waiter

    def _responseFailed(self, err, request):
        self.waiter.remove(request)

    def render_GET(self, request):
        request.setHeader("Content-Type", "application/json; charset=utf-8")
        if 'index' in request.args:
            index = request.args['index'][0]
            keys = self.events.keys()
            if index in keys:
                i = keys.index(index)
                k = keys[i + 1:]
                events = [{key: self.events[key]} for key in k]
                logger.debug("have events: {}".format(events))
                if events:
                    return json.dumps(events)
                elif 'wait' in request.args:
                    self.waiter.append(request)
                    request.notifyFinish().addErrback(
                        self._responseFailed, request)
                    return server.NOT_DONE_YET
        elif 'wait' in request.args:
            self.waiter.append(request)
            request.notifyFinish().addErrback(self._responseFailed, request)
            return server.NOT_DONE_YET
        return self.last_event()

    def last_event(self):
        if self.events:
            key = next(reversed(self.events))
            return json.dumps({key: self.events[key]})
        return json.dumps(self.events)


class HandlersResource(resource.Resource):

    isLeaf = False

    def __init__(self, corehandler):
        resource.Resource.__init__(self)
        self.corehandler = corehandler

    def getChild(self, handler, request):
        if handler == '':
            return self
        return HandlerResource(
            self.corehandler.handlers.get(handler, self.corehandler))

    def render_GET(self, request):
        request.setHeader("Access-Control-Allow-Origin", "*")
        request.setHeader("Content-Type", "application/json; charset=utf-8")
        return json.dumps(self.corehandler.handlers.keys())

class HandlerResource(resource.Resource):

    isLeaf = False

    def __init__(self, handler):
        resource.Resource.__init__(self)
        self.handler = handler

    def getChild(self, resource, request):
        if resource == '':
            return self
        if resource == 'tags':
            return AllTagsResource(self.handler)
        if resource == 'config':
            return ConfigResource(self.handler)
        return self

    def render_GET(self, request):
        request.setHeader("Content-Type", "application/json; charset=utf-8")
        request.setHeader("Access-Control-Allow-Origin", "*")
        return json.dumps(['tags', 'config'])

class ConfigResource(resource.Resource):

    isLeaf = True

    def __init__(self, handler):
        self.handler = handler
        resource.Resource.__init__(self)

    def render_GET(self, request):
        request.setHeader("Content-Type", "application/json; charset=utf-8")
        request.setHeader("Access-Control-Allow-Origin", "*")
        return json.dumps(self.handler.params)


class AllTagsResource(resource.Resource):

    isLeaf = False

    def __init__(self, handler):
        resource.Resource.__init__(self)
        self.handler = handler

    def getChild(self, tag, request):
        if tag == '':
            return self
        return TagResource(self.handler, tag)

    def render_GET(self, request):
        request.setHeader("Content-Type", "application/json; charset=utf-8")
        request.setHeader("Access-Control-Allow-Origin", "*")
        return json.dumps(self.handler.tags)


class TagResource(resource.Resource):

    isLeaf = True

    def __init__(self, handler, tag):
        resource.Resource.__init__(self)
        self.handler = handler
        self.tag = tag

    def render_GET(self, request):
        request.setHeader("Content-Type", "application/json; charset=utf-8")
        request.setHeader("Access-Control-Allow-Origin", "*")
        return json.dumps(self.handler.gettag(self.tag))

    def render_POST(self, request):
        request.setHeader("Content-Type", "application/json; charset=utf-8")
        request.setHeader("Access-Control-Allow-Origin", "*")
        data = {}
        try:
            content = request.content.read()
            data = json.loads(content)
        except:
            logger.debug("not json data: {}".format(content))
        data.update({key: request.args[key][0] for key in request.args})
        value = data.get('value', None)
        if value:
            self.handler.settag(self.tag, value)
        return json.dumps(self.handler.gettag(self.tag))


class smhs_web(resource.Resource):
    isLeaf = True
    action_get_json = "getJson"
    actionStopServer = "stopServer"
    action_list_tags = "listTags"
    action_set_tag = "setTag"

    def __init__(self, parent):
        env = Environment(loader=PackageLoader('pysmhs', 'www/templates'))
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
                last_handler = ""
                for tag in sorted(tags):
                    current_handler = tag.split('_')[0]
                    if current_handler != last_handler:
                        last_handler = current_handler
                    tag_name = tag.split('_')[1]
                    od.setdefault(last_handler, {})[tag_name] = str(tags[tag])
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

class monitor(resource.Resource):
    isLeaf = True

    def __init__(self, eventcache):
        env = Environment(loader=PackageLoader('www', 'templates'))
        self.eventcache = eventcache
        self.monitor_template = env.get_template('monitor_template.html')
        resource.Resource.__init__(self)

    def render_GET(self, request):
        return str(self.monitor_template.render(
            title=u'Monitor', description='here', events=self.eventcache))
