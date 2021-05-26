import json
import collectioncode.collect as collect
import collectioncode.process_srrgs as process_srrgs
import logging
import traceback
from server import clean_files as clean_files
import uuid
import time


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


def getallsrrgs():
    with open("jsonfiles/SRRG_db.json", 'r', encoding="utf8") as f:
        srrgs = json.load(f)
        f.close()
    all_srrgs = {}
    i = 1
    for srrg in srrgs['com.response-message']['com.data']['srrg.srrg-attributes']:
        tmp_srrg = {}
        tmp_srrg_resources_list = []
        tmp_name = "SRLG"+ str(i)
        tmp_srrg['SRLG-ID'] = str(srrg['srrg.srrg-id'])
        tmp_srrg['SRLG-Type'] = srrg['type-string']
        try:
            tmp_srrg_resources = srrg['srrg.resource-list']['srrg.resource']
            if isinstance(tmp_srrg_resources, dict):
                tmp_fdn = tmp_srrg_resources['srrg.resource-fdn']
                tmp_srrg_resources_list.append(tmp_fdn)
            elif isinstance(tmp_srrg_resources, list):
                for resource in tmp_srrg_resources:
                    tmp_srrg_resources_list.append(resource['srrg.resource-fdn'])
        except Exception as err:
            # srrg resource list is empty
            pass
        tmp_srrg['resources'] = tmp_srrg_resources_list
        all_srrgs[tmp_name] = tmp_srrg
        i += 1
    return json.dumps(all_srrgs)


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
    # with open("jsonfiles/topolinks_physical_db.json", 'r', encoding="utf8") as f:
    #     topo_links = json.load(f)
    #     f.close()
    # for key1, val1 in topo_links.items():
    #     for node in val1['Nodes']:
    #         if node['node'] == node_name:
    #             node_topo_links[key1+"-phy"] = val1
    if node_name == "":
        return json.dumps(topo_links)
    else:
        return json.dumps(node_topo_links)


def get_lc_srrgs(fdn):
    with open("jsonfiles/topolinks_add_drop_db.json", 'r', encoding="utf8") as f:
        topo_links = json.load(f)
        f.close()
    srrgs = []
    for key1, val1 in topo_links.items():
        if val1['fdn'] ==  fdn:
            for srrg in val1['srrgs-lc']:
                srrgs.append(srrg)
    return srrgs


def get_ad_srrgs(fdn):
    with open("jsonfiles/topolinks_add_drop_db.json", 'r', encoding="utf8") as f:
        topo_links = json.load(f)
        f.close()
    srrgs = []
    for key1, val1 in topo_links.items():
        if val1['fdn'] ==  fdn:
            for srrg in val1['srrgs-ad']:
                srrgs.append(srrg)
    return srrgs


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
        process_srrgs.processtopolinks_physical(region=global_region)
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


def assign_srrg(ajax_handler, request, global_region, baseURL, epnmuser, epnmpassword):
    try:
        pool_fdn = "MD=CISCO_EPNM!SRRGPL=" + request['pool-name']
        fdn_list = request['fdns']
        srrg_type = request['type']
        result = 'unknown'
        if srrg_type == "conduit":
            request_uuid = str(uuid.uuid4()).replace("-", "")
            result = process_srrgs.assign_srrg(baseURL, epnmuser, epnmpassword, pool_fdn, srrg_type, request_uuid,
                                               fdn_list)
        elif srrg_type == 'add-drop':
            tmp_srrgs = []
            fdns_to_assign_existing = []
            for tmp_fdn in fdn_list:
                fdn_assigned_srrgs = get_ad_srrgs(tmp_fdn)
                if len(fdn_assigned_srrgs) == 0:
                    fdns_to_assign_existing.append(tmp_fdn)
                else:
                    for tmp_srrg in fdn_assigned_srrgs:
                        tmp_srrgs.append(tmp_srrg)
            if len(tmp_srrgs) == 0:
                request_uuid = str(uuid.uuid4()).replace("-", "")
                result = process_srrgs.assign_srrg(baseURL, epnmuser, epnmpassword, pool_fdn, srrg_type, request_uuid,
                                                   fdn_list)
            else:
                srrg_fdn = tmp_srrgs[0]
                result = process_srrgs.assign_existing_srrg(baseURL,epnmuser,epnmpassword,srrg_fdn,fdns_to_assign_existing)

        elif srrg_type == "degree" or srrg_type == "l1node":
            for fdn in fdn_list:
                request_uuid = str(uuid.uuid4()).replace("-", "")
                single_fdn_list = [fdn]
                result = process_srrgs.assign_srrg(baseURL, epnmuser, epnmpassword, pool_fdn, srrg_type, request_uuid,
                                                   single_fdn_list)
        elif srrg_type == "line-card":
            tmp_srrgs = []
            fdns_to_assign_existing = []
            for tmp_fdn in fdn_list:
                fdn_assigned_srrgs = get_lc_srrgs(tmp_fdn['fdn'])
                if len(fdn_assigned_srrgs) == 0:
                    fdns_to_assign_existing.append(tmp_fdn['fdn'])
                else:
                    for tmp_srrg in fdn_assigned_srrgs:
                        tmp_srrgs.append(tmp_srrg)
            if len(tmp_srrgs) == 0:
                for i in range(0, 9):
                    chassis_num = "Chassis " + str(i)
                    for j in range(0, 16):
                        slot_num = "Slot " + str(j)
                        slot_fdns = []
                        for tmp_fdn in fdn_list:
                            if slot_num == tmp_fdn['slot'] and chassis_num == tmp_fdn['chassis']:
                                slot_fdns.append(tmp_fdn['fdn'])
                        if len(slot_fdns) > 0:
                            request_uuid = str(uuid.uuid4()).replace("-", "")
                            result = process_srrgs.assign_srrg(baseURL, epnmuser, epnmpassword, pool_fdn, srrg_type,
                                                               request_uuid, slot_fdns)

            else:
                srrg_fdn = tmp_srrgs[0]
                result = process_srrgs.assign_existing_srrg(baseURL,epnmuser,epnmpassword,srrg_fdn,fdns_to_assign_existing)

        if result == 'OPERATION_PARTIAL':
            status = 'partial'
        elif result == 'OPERATION_SUCCESSFUL':
            status = 'completed'
            time.sleep(10)
            collect.collectSRRGsOnly(baseURL, epnmuser, epnmpassword)
            process_srrgs.parse_ssrgs()
            logging.info("Region is " + str(global_region))
            process_srrgs.processl1nodes(region=global_region, type="Node")
            process_srrgs.processl1links(region=global_region, type="Degree")
            process_srrgs.processtopolinks(region=global_region)
            process_srrgs.processtopolinks_physical(region=global_region)
        else:
            status = 'failed'
        response = {'action': 'assign-srrg', 'status': status}
        logging.info(response)
        ajax_handler.write(json.dumps(response))
    except Exception as err:
        logging.info("Exception caught!!!")
        logging.info(err)
        response = {'action': 'assign-srrg', 'status': 'failed'}
        logging.info(response)
        ajax_handler.write(json.dumps(response))


def unassign_srrg(ajax_handler, request, global_region, baseURL, epnmuser, epnmpassword):
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
                process_srrgs.unassign_single_topolink_srrgs(baseURL, epnmuser, epnmpassword, tmp_fdn['fdn'],
                                                             srrg_type)
        time.sleep(10)
        collect.collectSRRGsOnly(baseURL, epnmuser, epnmpassword)
        process_srrgs.parse_ssrgs()
        logging.info("Region is " + str(global_region))
        process_srrgs.processl1nodes(region=global_region, type="Node")
        process_srrgs.processl1links(region=global_region, type="Degree")
        process_srrgs.processtopolinks(region=global_region)
        process_srrgs.processtopolinks_physical(region=global_region)
        response = {'action': 'unassign-srrg', 'status': 'completed'}
        logging.info(response)
        ajax_handler.write(json.dumps(response))
    except Exception as err:
        logging.warning("Exception during unassign-srrg operation!")
        response = {'action': 'unassign-srrg', 'status': 'failed'}
        logging.info(response)
        ajax_handler.write(json.dumps(response))


def delete_srrg( request, global_region, baseURL, epnmuser, epnmpassword):
    success = True
    response = {'action': 'delete-srrg', 'status': 'completed'}
    for srrg in request['srrgs']:
        tmp_fdn = "MD=CISCO_EPNM!SRRG=" + srrg
        result = process_srrgs.deleteSRRG(baseURL, epnmuser, epnmpassword, tmp_fdn)
        if result == False:
            success = False
            response = {'action': 'delete-srrg', 'status': 'failed'}
    return response
