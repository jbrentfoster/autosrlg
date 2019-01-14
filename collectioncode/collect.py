import collectioncode.utils
import time
import re
import json
import logging
import sys
import shutil


def runcollector(baseURL, epnmuser, epnmpassword):
    logging.info("Collecting L1 nodes...")
    collectL1Nodes_json(baseURL, epnmuser, epnmpassword)
    logging.info("Collecting 4k nodes...")
    collect4kNodes_json(baseURL, epnmuser, epnmpassword)
    logging.info("Collecting L1 links...")
    collectL1links_json(baseURL, epnmuser, epnmpassword)
    logging.info("Collecting SRRGs...")
    collectSRRGs_json(baseURL, epnmuser, epnmpassword)
    logging.info("Collecting SRRG pools...")
    collectSRRG_pools_json(baseURL, epnmuser, epnmpassword)
    logging.info("Collecting Topological Links...")
    collectTopoLinks_json(baseURL, epnmuser, epnmpassword)

def collectSRRGsOnly(baseURL, epnmuser, epnmpassword):
    logging.info("Collecting SRRGs...")
    collectSRRGs_json(baseURL, epnmuser, epnmpassword)
    logging.info("Collecting SRRG pools...")
    collectSRRG_pools_json(baseURL, epnmuser, epnmpassword)

def collectL1Nodes_json(baseURL, epnmuser, epnmpassword):
    incomplete = True
    startindex = 0
    jsonmerged = {}
    while incomplete:
        uri = "/data/v1/cisco-resource-physical:node?product-series=Cisco Network Convergence System 2000 Series&.startIndex=" + str(
            startindex)
        jsonresponse = collectioncode.utils.rest_get_json(baseURL, uri, epnmuser, epnmpassword)
        jsonaddition = json.loads(jsonresponse)
        firstindex = jsonaddition['com.response-message']['com.header']['com.firstIndex']
        lastindex = jsonaddition['com.response-message']['com.header']['com.lastIndex']
        if (lastindex - firstindex) == 99 and lastindex != -1:
            startindex += 100
        else:
            incomplete = False
        merge(jsonmerged, jsonaddition)

    with open("jsongets/l1-nodes.json", 'w', encoding="utf8") as f:
        # f.write(json.dumps(jsonmerged, f, sort_keys=True, indent=4, separators=(',', ': ')))
        json.dump(jsonmerged, f, sort_keys=True, indent=4, separators=(',', ': '))
        f.close()
    with open("jsongets/l1-nodes.json", 'rb') as f:
        jsonresponse = f.read()
        f.close()

    thejson = json.loads(jsonresponse)

    l1nodes = {}
    i = 1
    with open("jsonfiles/l1-nodes_db.json", 'w', encoding="utf8") as f:
        for node in thejson['com.response-message']['com.data']['nd.node']:
            if node['nd.product-series'] == "Cisco Network Convergence System 2000 Series":
                nodeName = node['nd.name']
                fdn = node['nd.fdn']
                logging.info("Processing node " + nodeName)
                try:
                    latitude = node['nd.latitude']
                    longitude = node['nd.longitude']
                except KeyError:
                    logging.error(
                        "Could not get longitude or latitidude for node " + nodeName + ".  Setting to 0.0 and 0.0")
                    latitude = {'fdtn.double-amount': 0.0, 'fdtn.units': 'DEGREES_DECIMAL'}
                    longitude = {'fdtn.double-amount': 0.0, 'fdtn.units': 'DEGREES_DECIMAL'}
                l1nodes['Node' + str(i)] = dict(
                    [('Name', nodeName), ('fdn', fdn), ('Latitude', latitude), ('Longitude', longitude)])
                i += 1
        # f.write(json.dumps(l1nodes, f, sort_keys=True, indent=4, separators=(',', ': ')))
        json.dump(l1nodes, f, sort_keys=True, indent=4, separators=(',', ': '))
        f.close()


def collect4kNodes_json(baseURL, epnmuser, epnmpassword):
    incomplete = True
    startindex = 0
    jsonmerged = {}
    while incomplete:
        uri = "/data/v1/cisco-resource-physical:node?product-series=Cisco Network Convergence System 4000 Series&.startIndex=" + str(
            startindex)
        jsonresponse = collectioncode.utils.rest_get_json(baseURL, uri, epnmuser, epnmpassword)
        jsonaddition = json.loads(jsonresponse)
        firstindex = jsonaddition['com.response-message']['com.header']['com.firstIndex']
        lastindex = jsonaddition['com.response-message']['com.header']['com.lastIndex']
        if (lastindex - firstindex) == 99 and lastindex != -1:
            startindex += 100
        else:
            incomplete = False
        merge(jsonmerged, jsonaddition)

    with open("jsongets/4k-nodes.json", 'w', encoding="utf8") as f:
        # f.write(json.dumps(jsonmerged, f, sort_keys=True, indent=4, separators=(',', ': ')))
        json.dump(jsonmerged, f, sort_keys=True, indent=4, separators=(',', ': '))
        f.close()
    with open("jsongets/4k-nodes.json", 'rb') as f:
        jsonresponse = f.read()
        f.close()

    thejson = json.loads(jsonresponse)

    l1nodes = {}
    i = 1
    with open("jsonfiles/4k-nodes_db.json", 'w', encoding="utf8") as f:
        for node in thejson['com.response-message']['com.data']['nd.node']:
            if node['nd.product-series'] == "Cisco Network Convergence System 4000 Series":
                nodeName = node['nd.name']
                fdn = node['nd.fdn']
                logging.info("Processing node " + nodeName)
                try:
                    latitude = node['nd.latitude']
                    longitude = node['nd.longitude']
                except KeyError:
                    logging.error(
                        "Could not get longitude or latitidude for node " + nodeName + ".  Setting to 0.0 and 0.0")
                    latitude = {'fdtn.double-amount': 0.0, 'fdtn.units': 'DEGREES_DECIMAL'}
                    longitude = {'fdtn.double-amount': 0.0, 'fdtn.units': 'DEGREES_DECIMAL'}
                l1nodes['Node' + str(i)] = dict(
                    [('Name', nodeName), ('fdn', fdn), ('Latitude', latitude), ('Longitude', longitude)])
                i += 1
        # f.write(json.dumps(l1nodes, f, sort_keys=True, indent=4, separators=(',', ': ')))
        json.dump(l1nodes, f, sort_keys=True, indent=4, separators=(',', ': '))
        f.close()


def collectL1links_json(baseURL, epnmuser, epnmpassword):
    incomplete = True
    startindex = 0
    jsonmerged = {}
    while incomplete:
        uri = "/data/v1/cisco-resource-network:topological-link?topo-layer=ots-link-layer&.startIndex=" + str(
            startindex)
        jsonresponse = collectioncode.utils.rest_get_json(baseURL, uri, epnmuser, epnmpassword)
        jsonaddition = json.loads(jsonresponse)
        firstindex = jsonaddition['com.response-message']['com.header']['com.firstIndex']
        lastindex = jsonaddition['com.response-message']['com.header']['com.lastIndex']
        if (lastindex - firstindex) == 99 and lastindex != -1:
            startindex += 100
        else:
            incomplete = False
        merge(jsonmerged, jsonaddition)

    with open("jsongets/l1-links.json", 'w', encoding="utf8") as f:
        # f.write(json.dumps(jsonmerged, f, sort_keys=True, indent=4, separators=(',', ': ')))
        json.dump(jsonmerged, f, sort_keys=True, indent=4, separators=(',', ': '))
        f.close()
    with open("jsongets/l1-links.json", 'rb') as f:
        jsonresponse = f.read()
        f.close()

    thejson = json.loads(jsonresponse)

    l1links = {}
    i = 1
    with open("jsonfiles/l1-links_db.json", 'w', encoding="utf8") as f:
        for link in thejson['com.response-message']['com.data']['topo.topological-link']:
            fdn = link['topo.fdn']
            logging.info("Processing link " + fdn)
            nodes = []
            endpointlist = link['topo.endpoint-list']['topo.endpoint']

            if len(endpointlist) > 1:
                for ep in endpointlist:
                    endpoint = ep['topo.endpoint-ref']
                    node = endpoint.split('!')[1].split('=')[1]
                    nodes.append(node)
                if len(nodes) > 1:
                    duplicates = False
                    if not duplicates:
                        l1links['Link' + str(i)] = dict([('fdn', fdn)])
                        l1links['Link' + str(i)]['Nodes'] = nodes
                    i += 1
        # f.write(json.dumps(l1links, f, sort_keys=True, indent=4, separators=(',', ': ')))
        json.dump(l1links, f, sort_keys=True, indent=4, separators=(',', ': '))
        f.close()


def collectSRRGs_json(baseURL, epnmuser, epnmpassword):
    incomplete = True
    startindex = 0
    jsonmerged = {}
    while incomplete:
        uri = "/data/v1/cisco-resource-network:shared-risk-resource-group?.startIndex=" + str(startindex)
        jsonresponse = collectioncode.utils.rest_get_json(baseURL, uri, epnmuser, epnmpassword)
        jsonaddition = json.loads(jsonresponse)
        firstindex = jsonaddition['com.response-message']['com.header']['com.firstIndex']
        lastindex = jsonaddition['com.response-message']['com.header']['com.lastIndex']
        if (lastindex - firstindex) == 99 and lastindex != -1:
            startindex += 100
            merge(jsonmerged, jsonaddition)
        else:
            incomplete = False
        # merge(jsonmerged, jsonaddition)

    with open("jsongets/SRRGs.json", 'w', encoding="utf8") as f:
        # f.write(json.dumps(jsonmerged, f, sort_keys=True, indent=4, separators=(',', ': ')))
        json.dump(jsonmerged, f, sort_keys=True, indent=4, separators=(',', ': '))
        f.close()

def collectSRRG_pools_json(baseURL, epnmuser, epnmpassword):
    incomplete = True
    startindex = 0
    jsonmerged = {}
    while incomplete:
        uri = "/data/v1/cisco-resource-network:srrg-pool?.startIndex=" + str(startindex)
        jsonresponse = collectioncode.utils.rest_get_json(baseURL, uri, epnmuser, epnmpassword)
        jsonaddition = json.loads(jsonresponse)
        firstindex = jsonaddition['com.response-message']['com.header']['com.firstIndex']
        lastindex = jsonaddition['com.response-message']['com.header']['com.lastIndex']
        if (lastindex - firstindex) == 99 and lastindex != -1:
            startindex += 100
        else:
            incomplete = False
        merge(jsonmerged, jsonaddition)

    with open("jsongets/SRRG_pools.json", 'w', encoding="utf8") as f:
        # f.write(json.dumps(jsonmerged, f, sort_keys=True, indent=4, separators=(',', ': ')))
        json.dump(jsonmerged, f, sort_keys=True, indent=4, separators=(',', ': '))
        f.close()

# def collectSRRG(baseURL, epnmuser, epnmpassword, srrg):
#     fdn = "fdn=MD=CISCO_EPNM!SRRG=" + srrg
#     uri = "/data/v1/cisco-resource-network:shared-risk-resource-group?" + fdn
#     jsonresponse = collectioncode.utils.rest_get_json(baseURL, uri, epnmuser, epnmpassword)
#     return jsonresponse


def collectTopoLinks_json(baseURL, epnmuser, epnmpassword):
    incomplete = True
    startindex = 0
    jsonmerged = {}
    while incomplete:
        uri = "/data/v1/cisco-resource-network:topological-link?topo-layer=och-link-layer&.startIndex=" + str(
            startindex)
        jsonresponse = collectioncode.utils.rest_get_json(baseURL, uri, epnmuser, epnmpassword)
        jsonaddition = json.loads(jsonresponse)
        firstindex = jsonaddition['com.response-message']['com.header']['com.firstIndex']
        lastindex = jsonaddition['com.response-message']['com.header']['com.lastIndex']
        if (lastindex - firstindex) == 99 and lastindex != -1:
            startindex += 100
        else:
            incomplete = False
        merge(jsonmerged, jsonaddition)

    with open("jsongets/topo-links.json", 'w', encoding="utf8") as f:
        # f.write(json.dumps(jsonmerged, f, sort_keys=True, indent=4, separators=(',', ': ')))
        json.dump(jsonmerged, f, sort_keys=True, indent=4, separators=(',', ': '))
        f.close()

    thejson = json.loads(jsonresponse)

    topolinks = {}
    i = 1
    with open("jsonfiles/topolinks_add_drop_db.json", 'w', encoding="utf8") as f:
        for link in thejson['com.response-message']['com.data']['topo.topological-link']:
            fdn = link['topo.fdn']
            logging.info("Processing topological link " + fdn)
            nodes = []
            endpointlist = link['topo.endpoint-list']['topo.endpoint']

            if len(endpointlist) > 1:
                for ep in endpointlist:
                    endpoint = ep['topo.endpoint-ref']
                    # print "Endpoint is: " + endpoint
                    node = endpoint.split('!')[1].split('=')[1]
                    ctp = endpoint.split('!')[2].split('=')[2]
                    # MD=CISCO_EPNM!ND=NCS4K-Site3!CTP=name=Optics0/5/0/11;lr=lr-optical-section
                    entry = {'node': node, 'ctp': ctp}
                    nodes.append(entry)
                if len(nodes) > 1:
                    topolinks['Link' + str(i)] = dict([('fdn', fdn)])
                    topolinks['Link' + str(i)]['Nodes'] = nodes
                i += 1
            # try:
            #     latitude = node['nd.latitude']
            #     longitude = node['nd.longitude']
            # except KeyError:
            #     logging.error("Could not get longitude or latitidude for node " + nodeName + ".  Setting to 0.0 and 0.0")
            #     latitude = {'fdtn.double-amount': 0.0, 'fdtn.units': 'DEGREES_DECIMAL'}
            #     longitude = {'fdtn.double-amount': 0.0, 'fdtn.units': 'DEGREES_DECIMAL'}
            # l1nodes['Node' + str(i)] = dict([('Name', nodeName), ('fdn',fdn), ('Latitude', latitude), ('Longitude', longitude)])
            # i += 1
        # f.write(json.dumps(topolinks, f, sort_keys=True, indent=4, separators=(',', ': ')))
        json.dump(topolinks, f, sort_keys=True, indent=4, separators=(',', ': '))
        f.close()
    # try:
    #     shutil.copy('jsonfiles/topolinks_add_drop_db.json', 'jsonfiles/topolinks_line_card_db.json')
    # except Exception as err:
    #     logging.info("No log file to copy...")


def merge(a, b):
    "merges b into a"
    for key in b:
        if key in a:  # if key is in both a and b
            if isinstance(a[key], dict) and isinstance(b[key], dict):  # if the key is dict Object
                merge(a[key], b[key])
            else:
                a[key] = a[key] + b[key]
        else:  # if the key is not in dict a , add it to dict a
            a.update({key: b[key]})
    return a
