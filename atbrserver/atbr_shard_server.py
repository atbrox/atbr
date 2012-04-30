__author__ = 'amund'

import tornado.web
import tornado.websocket
import os
import atbr.atbr
import logging
import sys
import json
from websocket import create_connection
import traceback

shards = {}

class AtbrShardGetWebsocketHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, application, request):
        tornado.websocket.WebSocketHandler.__init__(self, application, request)

    def on_message(self, message):
        try:
            print "getting message"
            global shards

            results = []
            for i, shard in enumerate(shards.keys()):
                print "i, shard = ", i, shard
                shards[shard].send(message)
                print "after sending message.."
                result = shards[shard].recv()
                print "result from shard %d = '%s'" % (i, result)
                results.append(result)

            self.write_message(json.dumps(results))
        except Exception, e:
            logging.error([e])

    def on_close(self):
        pass


def init_tornado(port_number):
    settings = {
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
        "cookie_secret": "lkjsdflkjdslkjsdflkjsdlfkjslkjfdslkjfjds",
        #"login_url": "/login",
        "xsrf_cookies": False
    }
    application = tornado.web.Application([
        (r'/getws/', AtbrShardGetWebsocketHandler),

    ], **settings)
    application.listen(port_number)
    tornado.ioloop.IOLoop.instance().start()

def init_shards(argv):
    global shards
    for i, atbr_server in enumerate(argv[1:]):
        # assuming host:port
        print "Creating websocket connection to shard number ", i, " at ", atbr_server
        websocket_address = "ws://%s/getws/" % (atbr_server)
        print "Connecting shard %d to websocket address '%s'" % (i,websocket_address)
        shards[atbr_server] = create_connection(websocket_address)

def main(argv):
    try:
        if len(argv) > 1:
            init_shards(argv)
            init_tornado(port_number=9999)
        else:
            print "\nError: no shard hosts provided!"
            print "\nUsage: python %s host_shard_1:port1 host_shard_2:port2 .." % (argv[0])
    except Exception, e:
        #traceback.print_exc()
        print "Error: ", e
        print "\nUsage: python %s host_shard_1:port1 host_shard_2:port2 .." % (argv[0])

if __name__ == "__main__":
    main(sys.argv)
