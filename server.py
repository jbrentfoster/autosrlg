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
epnmipaddr = "10.135.7.223"
baseURL = "https://" + epnmipaddr + "/restconf"
epnmuser = "root"
epnmpassword = "Epnm1234"
open_websockets = []
global_region = 1


class IndexHandler(tornado.web.RequestHandler):

    async def get(self):
        self.render("templates/index.html", port=args.port, epnm_ip=epnmipaddr, epnm_user=epnmuser,
                    epnm_pass=epnmpassword, region=global_region)

    # async def get(self):
    #     http = tornado.httpclient.AsyncHTTPClient()
    #     response = await http.fetch("http://friendfeed-api.com/v2/feed/bret")
    #     json = tornado.escape.json_decode(response.body)
    #     self.write("Fetched " + str(len(json["entries"])) + " entries "
    #                "from the FriendFeed API")


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

        if action == 'collect':
            methods.collection(self, request, global_region, baseURL, epnmuser, epnmpassword)
        elif action == 'assign-srrg':
            try:
                pool_fdn = "MD=CISCO_EPNM!SRRGPL=" + request['pool-name']
                fdn_list = request['fdns']
                srrg_type = request['type']
                if srrg_type == "conduit" or srrg_type == 'add-drop':
                    request_uuid = str(uuid.uuid4()).replace("-", "")
                    process_srrgs.assign_srrg(baseURL, epnmuser, epnmpassword, pool_fdn, srrg_type, request_uuid,
                                              fdn_list)
                elif srrg_type == "degree" or srrg_type == "l1node":
                    for fdn in fdn_list:
                        request_uuid = str(uuid.uuid4()).replace("-", "")
                        single_fdn_list = [fdn]
                        process_srrgs.assign_srrg(baseURL, epnmuser, epnmpassword, pool_fdn, srrg_type, request_uuid,
                                                  single_fdn_list)
                elif srrg_type == "line-card":
                    for i in range (0,9):
                        chassis_num = "Chassis " + str(i)
                        for j in range(0,16):
                            slot_num = "Slot " + str(j)
                            slot_fdns = []
                            for tmp_fdn in fdn_list:
                                if slot_num == tmp_fdn['slot'] and chassis_num == tmp_fdn['chassis']:
                                    slot_fdns.append(tmp_fdn['fdn'])
                            if len(slot_fdns) > 0:
                                request_uuid = str(uuid.uuid4()).replace("-", "")
                                process_srrgs.assign_srrg(baseURL, epnmuser, epnmpassword, pool_fdn, srrg_type, request_uuid,
                                                          slot_fdns)
                time.sleep(10)
                collect.collectSRRGsOnly(baseURL, epnmuser, epnmpassword)
                process_srrgs.parse_ssrgs()
                logging.info("Region is " + str(global_region))
                process_srrgs.processl1nodes(region=global_region, type="Node")
                process_srrgs.processl1links(region=global_region, type="Degree")
                process_srrgs.processtopolinks(region=global_region)
                response = {'action': 'assign-srrg', 'status': 'completed'}
                logging.info(response)
                self.write(json.dumps(response))
            except Exception as err:
                logging.info("Exception caught!!!")
                logging.info(err)
                response = {'action': 'assign-srrg', 'status': 'failed'}
                logging.info(response)
                self.write(json.dumps(response))
        elif action == 'unassign-srrg':
            try:
                type = request['type']
                if type == 'conduit':
                    srrg_type = 'srrgs-conduit'
                elif type == 'link' or type == 'l1node':
                    srrg_type = 'srrgs'
                elif type == 'add-drop':
                    srrg_type = 'srrgs-ad'
                elif type == 'line-card':
                    srrg_type = 'srrgs-lc'
                fdn_list = request['fdns']
                if type == 'conduit' or type == 'link':
                    for fdn in fdn_list:
                        process_srrgs.unassign_single_l1link_srrgs(baseURL, epnmuser, epnmpassword, fdn, srrg_type)
                elif type == 'l1node':
                    for fdn in fdn_list:
                        process_srrgs.unassign_single_l1node_srrgs(baseURL, epnmuser, epnmpassword, fdn, srrg_type)
                elif type == 'add-drop':
                    for fdn in fdn_list:
                        process_srrgs.unassign_single_topolink_srrgs(baseURL, epnmuser, epnmpassword, fdn, srrg_type)
                elif type == "line-card":
                    for tmp_fdn in fdn_list:
                            process_srrgs.unassign_single_topolink_srrgs(baseURL, epnmuser, epnmpassword, tmp_fdn['fdn'], srrg_type)
                time.sleep(10)
                collect.collectSRRGsOnly(baseURL, epnmuser, epnmpassword)
                process_srrgs.parse_ssrgs()
                logging.info("Region is " + str(global_region))
                process_srrgs.processl1nodes(region=global_region, type="Node")
                process_srrgs.processl1links(region=global_region, type="Degree")
                process_srrgs.processtopolinks(region=global_region)
                response = {'action': 'unassign-srrg', 'status': 'success'}
                logging.info(response)
                self.write(json.dumps(response))
            except Exception as err:
                logging.warning("Exception during unassign-srrg operation!")
                response = {'action': 'unassign-srrg', 'status': 'failed'}
                logging.info(response)
                self.write(json.dumps(response))
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
            response = {'action': 'update-epnm', 'status': 'success'}
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
        topo_links = methods.gettopolinks_psline(self.get_argument('l1node'), self.get_argument('psline'))
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

class DummyHandler(tornado.web.RequestHandler):

    def get(self):
        print(self.get_argument('foo', default="anna"))
        print(self.get_argument('bar', default="leigh"))
        pass


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
                url(r'/ajax', AjaxHandler, name="ajax"),
                url(r'/dummy/?', DummyHandler),
                # url(r'/ajax/updates', AjaxUpdatesHandler, name="ajax_updates")
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
