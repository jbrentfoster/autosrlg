"""
Creates an HTTP server with basic websocket communication.
"""
import argparse
import json
import os
import traceback
import webbrowser

import tornado.web
import tornado.websocket
from tornado.web import url

import methods


def main():
    settings = {
        # "static_path": os.path.join(os.path.dirname(__file__), "static"),
        "static_path": os.path.normpath(os.path.dirname(__file__)),
        # "cookie_secret": "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
        # "login_url": "/login",
        # "xsrf_cookies": True,
    }

    handlers = [url(r"/", IndexHandler, name="home"),
                url(r"/websocket", WebSocket),
                url(r'/static/(.*)',
                    tornado.web.StaticFileHandler,
                    dict(path=settings['static_path'])),
                # {'path': os.path.normpath(os.path.dirname(__file__))}),
                url(r'/srlg/([0-9]+)', SRLGHandler),
                url(r'/srlg/static/(.*)',
                    tornado.web.StaticFileHandler,
                    dict(path=settings['static_path'])),
                url(r'/l1links',L1LinksHandler, name="l1_links"),
                url(r'/l1nodes', L1NodesHandler, name="l1_nodes"),
                url(r'/topolinks', TopoLinksHandler, name="topo_links"),
                url(r'/ajax', AjaxHandler, name="ajax")
                ]

    application = tornado.web.Application(handlers)
    application.listen(args.port)

    # webbrowser.open("http://localhost:%d/" % args.port, new=2)

    tornado.ioloop.IOLoop.instance().start()


class IndexHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("templates/index.html", port=args.port)

class AjaxHandler(tornado.web.RequestHandler):
    """Post a new message to the chat room."""

    def post(self):
        foo = self.get_argument("firstname")
        bar = self.get_argument("lastname")
        response = {"first": foo, "last": bar}
        print(foo+bar)
        self.write(response)
        # message = {"id": str(uuid.uuid4()), "body": self.get_argument("body")}

class SRLGHandler(tornado.web.RequestHandler):

    def get(self, srlg_num):
        # self.write("SRLG is : " + srlg_num)
        home_url = self.reverse_url("home")
        self.render("templates/srlg_template.html", port=args.port, srlg_num=srlg_num, home_url=home_url)

class L1NodesHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("templates/l1_nodes_template.html", port=args.port)

class L1LinksHandler(tornado.web.RequestHandler):

    def get(self):
        # full_url = self.request.full_url()
        # uri = self.request.uri
        base_full_url = self.request.protocol + "://" + self.request.host
        links_table = methods.getl1links(base_full_url)
        self.render("templates/l1_links_template.html", port=args.port, links_table_contents = links_table)

class TopoLinksHandler(tornado.web.RequestHandler):

    def get(self):
        topo_links = methods.gettopolinks()
        self.render("templates/topo_links_template.html", port=args.port, topo_links_data = topo_links)

class WebSocket(tornado.websocket.WebSocketHandler):

    def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        """Evaluates the function pointed to by json-rpc."""
        json_rpc = json.loads(message)
        print "Websocket received message: " + json.dumps(json_rpc)

        try:
            # The only available method is `count`, but I'm generalizing
            # to allow other methods without too much extra code
            result = getattr(methods,
                             json_rpc["method"])(**json_rpc["params"])
            error = None
        except:
            # Errors are handled by enabling the `error` flag and returning a
            # stack trace. The client can do with it what it will.
            result = traceback.format_exc()
            error = 1

        json_rpc_response = json.dumps({"result": result, "error": error,
                                        "id": json_rpc["id"]},
                                       separators=(",", ":"))
        print "Websocket replied with message: " + json_rpc_response
        self.write_message(json_rpc_response)

    def on_close(self):
        print("WebSocket closed!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Starts a webserver for stuff.")
    parser.add_argument("--port", type=int, default=8000, help="The port on which "
                                                               "to serve the website.")
    args = parser.parse_args()
    main()
