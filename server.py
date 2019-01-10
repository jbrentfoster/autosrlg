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
import tornado.escape
import tornado.ioloop
import tornado.locks
from tornado.web import url
import uuid
import methods
import collectioncode.collect as collect
import asyncio
import collectioncode.process_srrgs as process_srrgs
import logging
from distutils.dir_util import copy_tree
from distutils.dir_util import remove_tree
from distutils.dir_util import mkpath



# epnmipaddr = args.epnm_ipaddr
epnmipaddr = "10.135.7.222"
baseURL = "https://" + epnmipaddr + "/restconf"
# epnmuser = args.epnm_user
# epnmpassword = args.epnm_pass
epnmuser = "root"
epnmpassword = "Epnm1234"
open_websockets = []

class IndexHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("templates/index.html", port=args.port)

class AjaxHandler(tornado.web.RequestHandler):

    async def post(self):
        # message = {"id": str(uuid.uuid4()), "body": self.get_argument("body")}
        # foo = self.get_argument("firstname")
        # bar = self.get_argument("lastname")
        # response = {"first": foo, "last": bar}
        # print(foo+bar)
        message = tornado.escape.recursive_unicode(self.request.arguments)
        # moo = self.request.arguments
        # goo  = tornado.escape.recursive_unicode(self.request.arguments)
        # foo = tornado.escape.json_decode(self.request.arguments)
        # bar = json.loads(self.request.body.decode('utf-8'))
        print(json.dumps(message))
        action = message['action'][0]
        region = message['region'][0]
        srlg_only = message['srlg-only'][0]
        region_int = int(region)

        if action == 'collect':
            try:
                # clean_files()
                self.send_message_open_ws("Collecting data from EPNM...")
                if srlg_only == 'on':
                    collect.collectSRRGsOnly(baseURL, epnmuser, epnmpassword)
                else:
                    collect.runcollector(baseURL, epnmuser, epnmpassword)
                self.send_message_open_ws("Processing SRLGs...")
                process_srrgs.parse_ssrgs()
                self.send_message_open_ws("Processing nodes, links, topolinks...")
                process_srrgs.processl1nodes(region=region_int, type="Node")
                process_srrgs.processl1links(region=region_int, type="Degree")
                process_srrgs.processtopolinks(region=region_int)
                response = {'action': 'collect', 'status': 'completed'}
            except Exception as err:
                print("Exception caught!!!")
                print(err)
                response = {'action': 'collect', 'status': 'failed'}
        self.write(json.dumps(response))

    def send_message_open_ws(self, message):
        for ws in open_websockets:
            ws.send_message(message)

class SRLGHandler(tornado.web.RequestHandler):

    def get(self, srlg_num):
        srlg = methods.getsrlg(srlg_num)
        self.render("templates/srlg_template.html", port=args.port, srlg_num=srlg_num, srlg_data=srlg)

class L1NodesHandler(tornado.web.RequestHandler):

    def get(self):
        l1nodes = methods.getl1nodes()
        self.render("templates/l1_nodes_template.html", port=args.port, l1nodes_data=l1nodes)

class L1LinksHandler(tornado.web.RequestHandler):

    def get(self):
        # full_url = self.request.full_url()
        # uri = self.request.uri
        # base_full_url = self.request.protocol + "://" + self.request.host
        l1links = methods.getl1links()
        self.render("templates/l1_links_template.html", port=args.port, l1links_data=l1links)

class TopoLinksHandler(tornado.web.RequestHandler):

    def get(self):
        topo_links = methods.gettopolinks()
        self.render("templates/topo_links_template.html", port=args.port, topo_links_data=topo_links)

class WebSocket(tornado.websocket.WebSocketHandler):

    def open(self):
        print("WebSocket opened")
        open_websockets.append(self)

    def send_message(self, message):
        self.write_message(message)
        pass

    def on_message(self, message):
        """Evaluates the function pointed to by json-rpc."""
        json_rpc = json.loads(message)
        print ("Websocket received message: " + json.dumps(json_rpc))

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
        print ("Websocket replied with message: " + json_rpc_response)
        self.write_message(json_rpc_response)

    def on_close(self):
        open_websockets.remove(self)
        print("WebSocket closed!")


def main():
    # Set up logging
    try:
        os.remove('collection.log')
    except Exception as err:
        print("No log file to delete...")

    logFormatter = logging.Formatter('%(levelname)s:  %(message)s')
    rootLogger = logging.getLogger()
    rootLogger.level = logging.INFO

    fileHandler = logging.FileHandler(filename='collection.log')
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)

    logging.info("Starting webserver...")
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
                url(r'/ajax', AjaxHandler, name="ajax"),
                # url(r'/ajax/updates', AjaxUpdatesHandler, name="ajax_updates")
                ]

    application = tornado.web.Application(handlers)
    application.listen(args.port)

    # webbrowser.open("http://localhost:%d/" % args.port, new=2)

    tornado.ioloop.IOLoop.instance().start()

def clean_files():
    # Delete all output files
    logging.info("Cleaning files from last collection...")
    try:
        remove_tree('jsonfiles')
        remove_tree('jsongets')
    except Exception as err:
        logging.info("No files to cleanup...")

    # Recreate output directories
    mkpath('jsonfiles')
    mkpath('jsongets')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Starts a webserver for stuff.")
    parser.add_argument("--port", type=int, default=8000, help="The port on which "
                                                               "to serve the website.")
    args = parser.parse_args()
    main()
