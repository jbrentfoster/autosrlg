import json
import collectioncode.collect as collect
import collectioncode.process_srrgs as process_srrgs
import logging
import traceback
from server import clean_files as clean_files


# def count(number):
#     """It counts. Duh. Note: intentionally written to break on non-ints"""
#     return int(number) + 1

def getl1nodes():
    with open("jsonfiles/l1-nodes_db.json", 'r', ) as f:
        l1nodes = json.load(f)
        f.close()
    return json.dumps(l1nodes)

def getmplsnodes():
    with open("jsonfiles/4k-nodes_db.json", 'r', ) as f:
        mplsnodes = json.load(f)
        f.close()
    return json.dumps(mplsnodes)


def get_srrg_pools(pool_type):
    srrg_pools = []
    with open("jsongets/SRRG_pools.json", 'r', encoding="utf8") as f:
        pools = json.load(f)
        f.close()
    try:
        for pool in pools['com.response-message']['com.data']['srrg.srrg-pool-attributes']:
            if pool['srrg.type-id'] == pool_type:
                srrg_pools.append(pool['srrg.name'])
        return srrg_pools
    except Exception as err:
        return ['No SRLG Pool Defined']


def getsrlg(srlg):
    with open("jsonfiles/SRRG_db.json", 'r', encoding="utf8") as f:
        srrgs = json.load(f)
        f.close()
    for srrg in srrgs['com.response-message']['com.data']['srrg.srrg-attributes']:
        if str(srrg['srrg.srrg-id']) == srlg:
            return json.dumps(srrg)
    return None


def getl1links():
    with open("jsonfiles/l1-links_db.json", 'r', encoding="utf8") as f:
        l1links = json.load(f)
        f.close()
    return json.dumps(l1links)


def gettopolinks_psline(node_name, psline):
    with open("jsonfiles/topolinks_add_drop_db.json", 'r', encoding="utf8") as f:
        topo_links = json.load(f)
        f.close()
    node_topo_links = {}
    for key1, val1 in topo_links.items():
        for node in val1['Nodes']:
            if node['node'] == node_name:
                # logging.info('Checking topo link ' + val1['fdn'])
                ctp_split = node['ctp'].split('&')[0].split('-')
                node_psline = ctp_split[0] + '-' + ctp_split[1] + '-' + ctp_split[2]
                if node_psline == psline:
                    node_topo_links[key1] = val1
    if node_name == "":
        return json.dumps(topo_links)
    else:
        return json.dumps(node_topo_links)


def gettopolinks_mpls_node(node_name):
    with open("jsonfiles/topolinks_add_drop_db.json", 'r', encoding="utf8") as f:
        topo_links = json.load(f)
        f.close()
    node_topo_links = {}
    for key1, val1 in topo_links.items():
        for node in val1['Nodes']:
            if node['node'] == node_name:
                node_topo_links[key1] = val1
    if node_name == "":
        return json.dumps(topo_links)
    else:
        return json.dumps(node_topo_links)


def collection(ajax_handler, request, global_region, baseURL, epnmuser, epnmpassword):
    try:
        srlg_only = request['srlg-only']
        ajax_handler.send_message_open_ws("Collecting data from EPNM...")
        if srlg_only == 'on':
            collect.collectSRRGsOnly(baseURL, epnmuser, epnmpassword)
        elif srlg_only == 'off':
            clean_files()
            collect.runcollector(baseURL, epnmuser, epnmpassword)
        ajax_handler.send_message_open_ws("Processing SRLGs...")
        process_srrgs.parse_ssrgs()
        ajax_handler.send_message_open_ws("Processing nodes, links, topolinks...")
        process_srrgs.processl1nodes(region=global_region, type="Node")
        process_srrgs.processl1links(region=global_region, type="Degree")
        process_srrgs.processtopolinks(region=global_region)
        ajax_handler.send_message_open_ws("Completed collecting data from EPNM...")
        response = {'action': 'collect', 'status': 'completed'}
        logging.info(response)
        ajax_handler.write(json.dumps(response))
    except Exception as err:
        try:
            logging.info("Exception caught!!!")
            logging.info(err)
            response = {'action': 'collect', 'status': 'failed'}
            ajax_handler.write(json.dumps(response))
        finally:
            # Display the *original* exception
            traceback.print_tb(err.__traceback__)
