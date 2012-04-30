__author__ = 'amund'

import tornado.web
import tornado.websocket
import os
import atbr.atbr
import logging

key_value_store = atbr.atbr.Atbr()

class AtbrGetHttpHandler(tornado.web.RequestHandler):
    def get(self, key):
        try:
            assert key and type(key) == unicode
            global key_value_store
            key = str(key)
            self.write(key_value_store.get(key))
        except Exception, e:
            logging.error([e])

class AtbrGetWebsocketHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, application, request):
        tornado.websocket.WebSocketHandler.__init__(self, application, request)

    def on_message(self, message):
        try:
            assert message and type(message) == str
            global key_value_store
            self.write_message(key_value_store.get(message))
        except Exception, e:
            logging.error([e])

    def on_close(self):
        pass

class AtbrPutHttpHandler(tornado.web.RequestHandler):
    def get(self, key, value):
        try:
            assert key and type(key) == unicode
            assert value and type(value) == unicode
            global key_value_store
            key_value_store.put(str(key),str(value))
        except Exception, e:
            logging.error([e])

class AtbrPutWebsocketHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, application, request):
        tornado.websocket.WebSocketHandler.__init__(self, application, request)

    def on_message(self, message):
        try:
            assert message and type(message) == str
            (key, value) = message.split("\t")
            global key_value_store
            key_value_store.put(key, value)
        except Exception, e:
            logging.error([e])

    def on_close(self):
        pass

class AtbrLoadHttpHandler(tornado.web.RequestHandler):
    def get(self, filename):
        try:
            assert filename and type(filename) == unicode
            global key_value_store
            filename = str(filename)
            key_value_store.load(filename)
        except Exception, e:
            logging.error([e])

class AtbrLoadWebsocketHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, application, request):
        tornado.websocket.WebSocketHandler.__init__(self, application, request)

    def on_message(self, message):
        try:
            filename = str(message)
            global key_value_store
            key_value_store.load(filename)
        except Exception, e:
            logging.error([e])

    def on_close(self):
        pass

class AtbrSaveHttpHandler(tornado.web.RequestHandler):
    def get(self, filename):
        try:
            assert filename and type(filename) == unicode
            global key_value_store
            filename = str(filename)
            key_value_store.save(filename)
        except Exception, e:
            logging.error([e])

class AtbrSaveWebsocketHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, application, request):
        tornado.websocket.WebSocketHandler.__init__(self, application, request)

    def on_message(self, message):
        try:
            filename = str(message)
            global key_value_store
            key_value_store.save(filename)
        except Exception, e:
            logging.error([e])

    def on_close(self):
        pass

def main():
    settings = {
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
        "cookie_secret": "lkjsdflkjdslkjsdflkjsdlfkjslkjfdslkjfjds",
        #"login_url": "/login",
        "xsrf_cookies": False
    }

    application = tornado.web.Application([
        (r'/get/key/(.*)', AtbrGetHttpHandler),
        (r'/put/key/(.*)/value/(.*)', AtbrPutHttpHandler),
        (r'/load/(.*)', AtbrLoadHttpHandler),
        (r'/save/(.*)', AtbrSaveHttpHandler),
        (r'/getws/', AtbrGetWebsocketHandler),
        (r'/putws/', AtbrPutWebsocketHandler),
        (r'/loadws/', AtbrLoadWebsocketHandler),
        (r'/savews/', AtbrSaveWebsocketHandler),

    ], **settings)

    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
