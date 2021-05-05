"""
Creates an HTTP server with basic websocket communication.
"""
import argparse
from datetime import datetime
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
import methods
import logging
from distutils.dir_util import copy_tree
from distutils.dir_util import remove_tree
from distutils.dir_util import mkpath
import time

# global variables...
# epnmipaddr = args.epnm_ipaddr
# epnmuser = args.epnm_user
# epnmpassword = args.epnm_pass
epnmipaddr = "10.201.1.246"
baseURL = "https://" + epnmipaddr + "/restconf"
epnmuser = "root"
epnmpassword = "Public123"
open_websockets = []
global_region = 4


class IndexHandler(tornado.web.RequestHandler):

    async def get(self):
        self.render("templates/index.html", port=args.port, epnm_ip=epnmipaddr, epnm_user=epnmuser,
                    epnm_pass=epnmpassword, region=global_region)


class AjaxHandler(tornado.web.RequestHandler):

    async def post(self):
        global global_region
        global epnmipaddr
        global baseURL
        global epnmuser
        global epnmpassword

        request_body = self.request.body.decode("utf-8")
        # request = tornado.escape.recursive_unicode(self.request.arguments)
        logging.info("Received AJAX request..")
        logging.info(request_body)
        request = json.loads(request_body)

        try:
            action = request['action']
        except Exception as err:
            logging.warning("Invalid AJAX request")
            logging.warning(err)
            response = {'status': 'failed', 'error': err}
            logging.info(response)
            self.write(json.dumps(response))
            return

        if action == 'collect':
            methods.collection(self, request, global_region, baseURL, epnmuser, epnmpassword)
        elif action == 'assign-srrg':
            methods.assign_srrg(self, request, global_region, baseURL, epnmuser, epnmpassword)
        elif action == 'unassign-srrg':
            methods.unassign_srrg(self, request, global_region, baseURL, epnmuser, epnmpassword)
        elif action == 'get-l1nodes':
            l1nodes = methods.getl1nodes()
            self.write(json.dumps(l1nodes))
        elif action == 'get-l1links':
            l1links = methods.getl1links()
            self.write(json.dumps(l1links))
        elif action == 'get-topolinks':
            node_name = request['l1node']
            psline = request['psline']
            topolinks = methods.gettopolinks_psline(node_name, psline)
            self.write(json.dumps(topolinks))
        elif action == 'get-topolinks-line-card':
            node_name = request['mplsnode']
            topolinks = methods.gettopolinks_mpls_node(node_name)
            self.write(json.dumps(topolinks))
        elif action == 'update-epnm':
            time.sleep(2)
            epnmipaddr = request['epnm-ip']
            baseURL = "https://" + epnmipaddr + "/restconf"
            epnmuser = request['epnm-user']
            epnmpassword = request['epnm-pass']
            region = request['region']
            region_int = int(region)
            global_region = region_int
            response = {'action': 'update-epnm', 'status': 'completed'}
            logging.info(response)
            self.write(json.dumps(response))
        else:
            logging.warning("Received request for unknown operation!")
            response = {'status': 'unknown', 'error': "unknown request"}
            logging.info(response)
            self.write(json.dumps(response))

    def send_message_open_ws(self, message):
        for ws in open_websockets:
            ws.send_message(message)


class SRLGHandler(tornado.web.RequestHandler):

    def get(self, srlg_num):
        srlg = methods.getsrlg(srlg_num)
        self.render("templates/srlg_template.html", port=args.port, srlg_num=srlg_num, srlg_data=srlg)


class ROADMNodesHandler(tornado.web.RequestHandler):

    def get(self):
        l1nodes = methods.getl1nodes()
        pools = methods.get_srrg_pools(1)
        # if len(pools) == 0:
        #     pools = ['No Node SRLG Pools Defined']
        self.render("templates/roadm_nodes_template.html", port=args.port, l1nodes_data=l1nodes, pools=pools)


class ROADMLinksHandler(tornado.web.RequestHandler):

    def get(self):
        # full_url = self.request.full_url()
        # uri = self.request.uri
        # base_full_url = self.request.protocol + "://" + self.request.host
        l1links = methods.getl1links()
        conduit_pools = methods.get_srrg_pools(0)
        degree_pools = methods.get_srrg_pools(2)
        self.render("templates/roadm_links_template.html", port=args.port, degree_pools=degree_pools,
                    conduit_pools=conduit_pools, l1links_data=l1links)


class MPLSNodesHandler(tornado.web.RequestHandler):

    def get(self):
        mpls_nodes = methods.getmplsnodes()
        self.render("templates/mpls_nodes_template.html", port=args.port, mpls_nodes_data=mpls_nodes)


class AddDropTopoLinksHandler(tornado.web.RequestHandler):

    def get(self):
        l1node = self.get_argument('l1node')
        psline = self.get_argument('psline')
        topo_links = methods.gettopolinks_psline(l1node, psline)
        add_drop_pools = methods.get_srrg_pools(3)
        self.render("templates/topo_links_template_add_drop.html", port=args.port, topo_links_data=topo_links,
                    add_drop_pools=add_drop_pools, l1node=l1node)


class LineCardTopoLinksHandler(tornado.web.RequestHandler):

    def get(self):
        thequery = self.request.query
        mplsnode = thequery.split('=')[1]
        topo_links = methods.gettopolinks_mpls_node(mplsnode)
        card_pools = methods.get_srrg_pools(6)
        self.render("templates/topo_links_template_line_card.html", port=args.port, topo_links_data=topo_links,
                    card_pools=card_pools)


class WebSocket(tornado.websocket.WebSocketHandler):

    def open(self):
        logging.info("WebSocket opened")
        open_websockets.append(self)

    def send_message(self, message):
        self.write_message(message)

    def on_message(self, message):
        """Evaluates the function pointed to by json-rpc."""
        json_rpc = json.loads(message)
        logging.info("Websocket received message: " + json.dumps(json_rpc))

        try:
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
        logging.info("Websocket replied with message: " + json_rpc_response)
        self.write_message(json_rpc_response)

    def on_close(self):
        open_websockets.remove(self)
        logging.info("WebSocket closed!")


def main():
    # Set up logging
    try:
        os.remove('collection.log')
    except Exception as err:
        logging.info("No log file to delete...")

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
    current_time = str(datetime.now().strftime('%Y-%m-%d-%H%M-%S'))
    logging.info("Current time is: " + current_time)
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
                url(r'/roadmlinks', ROADMLinksHandler, name="roadm_links"),
                url(r'/roadmnodes', ROADMNodesHandler, name="roadm_nodes"),
                url(r'/mplsnodes', MPLSNodesHandler, name="mpls_nodes"),
                url(r'/topolinks-ad/?', AddDropTopoLinksHandler, name="ad-topo_links"),
                url(r'/topolinks-ad/static/(.*)',
                    tornado.web.StaticFileHandler,
                    dict(path=settings['static_path'])),
                url(r'/topolinks-lc/?', LineCardTopoLinksHandler, name="lc-topo_links"),
                url(r'/topolinks-lc/static/(.*)',
                    tornado.web.StaticFileHandler,
                    dict(path=settings['static_path'])),
                url(r'/ajax', AjaxHandler, name="ajax")
                ]

    application = tornado.web.Application(handlers)
    application.listen(args.port)

    # webbrowser.open("http://localhost:%d/" % args.port, new=2)

    # tornado.ioloop.IOLoop.instance().start()
    tornado.ioloop.IOLoop.current().start()


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
