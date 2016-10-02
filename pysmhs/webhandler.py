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
        root.putChild("api", ApiResource(parent, self.waiter, self.eventcache))
        #root.putChild("mon", monitor(self.eventcache))
        self.site = server.Site(root)

    def loadtags(self):
        pass

    def process(self, signal, event):
        webevent = {}
        for key, value in event.items():
            webevent['tag'] = key
            webevent['value'] = value
            webevent['handler'] = signal
        if len(self.eventcache) == self.cachemax:
            self.eventcache.popitem(last=False)
        self.addevent(webevent)

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
        request.setHeader("Access-Control-Allow-Origin", "*")
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
