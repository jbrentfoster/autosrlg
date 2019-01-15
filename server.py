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
import time

# global variables...
# epnmipaddr = args.epnm_ipaddr
# epnmuser = args.epnm_user
# epnmpassword = args.epnm_pass
epnmipaddr = "10.135.7.222"
baseURL = "https://" + epnmipaddr + "/restconf"
epnmuser = "root"
epnmpassword = "Epnm1234"
open_websockets = []
global_region = 1


class IndexHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("templates/index.html", port=args.port, epnm_ip=epnmipaddr, epnm_user=epnmuser,
                    epnm_pass=epnmpassword, region=global_region)


class AjaxHandler(tornado.web.RequestHandler):

    async def post(self):
        global global_region
        global epnmipaddr
        global baseURL
        global epnmuser
        global epnmpassword
        request = tornado.escape.recursive_unicode(self.request.arguments)
        logging.info("Received AJAX request..")
        logging.info(json.dumps(request))
        try:
            action = request['action'][0]
        except Exception as err:
            logging.warning("Invalid AJAX request")
            logging.warning(err)
            response = {'status': 'failed', 'error': err}
            self.write(json.dumps(response))

        if action == 'collect':
            try:
                # region = request['region'][0]
                srlg_only = request['srlg-only'][0]
                # region_int = int(region)
                # global_region = region_int
                self.send_message_open_ws("Collecting data from EPNM...")
                if srlg_only == 'on':
                    collect.collectSRRGsOnly(baseURL, epnmuser, epnmpassword)
                elif srlg_only == 'off':
                    clean_files()
                    collect.runcollector(baseURL, epnmuser, epnmpassword)
                self.send_message_open_ws("Processing SRLGs...")
                process_srrgs.parse_ssrgs()
                self.send_message_open_ws("Processing nodes, links, topolinks...")
                process_srrgs.processl1nodes(region=global_region, type="Node")
                process_srrgs.processl1links(region=global_region, type="Degree")
                process_srrgs.processtopolinks(region=global_region)
                response = {'action': 'collect', 'status': 'completed'}
                logging.info(response)
                self.write(json.dumps(response))
            except Exception as err:
                logging.info("Exception caught!!!")
                logging.info(err)
                response = {'action': 'collect', 'status': 'failed'}
                self.write(json.dumps(response))
        elif action == 'assign-srrg':
            try:
                pool_fdn = "MD=CISCO_EPNM!SRRGPL=" + request['pool-name'][0]
                link_fdn_list = request['fdns[]']
                srrg_type = request['type'][0]
                if srrg_type == "conduit":
                    process_srrgs.assignl1link_srrg(baseURL, epnmuser, epnmpassword, pool_fdn, link_fdn_list)
                elif srrg_type == "degree" or srrg_type == "l1node":
                    for fdn in link_fdn_list:
                        single_fdn_list = [fdn]
                        process_srrgs.assignl1link_srrg(baseURL, epnmuser, epnmpassword, pool_fdn, single_fdn_list)
                collect.collectSRRGsOnly(baseURL, epnmuser, epnmpassword)
                process_srrgs.parse_ssrgs()
                logging.info("Region is " + str(global_region))
                process_srrgs.processl1nodes(region=global_region, type="Node")
                process_srrgs.processl1links(region=global_region, type="Degree")
                process_srrgs.processtopolinks(region=global_region)
                response = {'action': 'assign-srrg', 'status': 'completed'}
                self.write(json.dumps(response))
            except Exception as err:
                logging.info("Exception caught!!!")
                logging.info(err)
                response = {'action': 'assign-srrg', 'status': 'failed'}
                self.write(json.dumps(response))
        elif action == 'unassign-srrg':
            try:
                type = request['type'][0]
                if type == 'conduit':
                    srrg_type = 'srrgs-conduit'
                elif type == 'link' or type == 'l1node':
                    srrg_type = 'srrgs'
                fdn_list = request['fdns[]']
                if type == 'conduit' or type == 'link':
                    for fdn in fdn_list:
                        process_srrgs.unassign_single_l1link_srrgs(baseURL, epnmuser, epnmpassword, fdn, srrg_type)
                elif type == 'l1node':
                    for fdn in fdn_list:
                        process_srrgs.unassign_single_l1node_srrgs(baseURL, epnmuser, epnmpassword, fdn, srrg_type)
                collect.collectSRRGsOnly(baseURL, epnmuser, epnmpassword)
                process_srrgs.parse_ssrgs()
                logging.info("Region is " + str(global_region))
                process_srrgs.processl1nodes(region=global_region, type="Node")
                process_srrgs.processl1links(region=global_region, type="Degree")
                process_srrgs.processtopolinks(region=global_region)
                response = {'action': 'unassign-srrg', 'status': 'success'}
                self.write(json.dumps(response))
            except Exception as err:
                logging.warning("Exception during unassign-srrg operation!")
                response = {'action': 'unassign-srrg', 'status': 'fail'}
                self.write(json.dumps(response))
        elif action == 'get-l1nodes':
            l1nodes = methods.getl1nodes()
            logging.info(l1nodes)
            self.write(json.dumps(l1nodes))
        elif action == 'get-l1links':
            l1links = methods.getl1links()
            logging.info(l1links)
            self.write(json.dumps(l1links))
        elif action == 'update-epnm':
            time.sleep(2)
            epnmipaddr = request['epnm-ip'][0]
            baseURL = "https://" + epnmipaddr + "/restconf"
            epnmuser = request['epnm-user'][0]
            epnmpassword = request['epnm-pass'][0]
            region = request['region'][0]
            region_int = int(region)
            global_region = region_int
            response = {'action': 'update-epnm', 'status': 'success'}
            self.write(json.dumps(response))
        else:
            logging.warning("Received request for unknown operation!")
            response = {'status': 'unknown', 'error': "unknown request"}
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
        pools = methods.get_srrg_pools(1)
        self.render("templates/l1_nodes_template.html", port=args.port, l1nodes_data=l1nodes, pools=pools)


class L1LinksHandler(tornado.web.RequestHandler):

    def get(self):
        # full_url = self.request.full_url()
        # uri = self.request.uri
        # base_full_url = self.request.protocol + "://" + self.request.host
        l1links = methods.getl1links()
        conduit_pools = methods.get_srrg_pools(0)
        degree_pools = methods.get_srrg_pools(2)
        self.render("templates/l1_links_template.html", port=args.port, degree_pools=degree_pools, conduit_pools=conduit_pools, l1links_data=l1links)


class TopoLinksHandler(tornado.web.RequestHandler):

    def get(self):
        topo_links = methods.gettopolinks()
        self.render("templates/topo_links_template.html", port=args.port, topo_links_data=topo_links)


class WebSocket(tornado.websocket.WebSocketHandler):

    def open(self):
        logging.info("WebSocket opened")
        open_websockets.append(self)

    def send_message(self, message):
        self.write_message(message)
        pass

    def on_message(self, message):
        """Evaluates the function pointed to by json-rpc."""
        json_rpc = json.loads(message)
        logging.info("Websocket received message: " + json.dumps(json_rpc))

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
                url(r'/l1links', L1LinksHandler, name="l1_links"),
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
