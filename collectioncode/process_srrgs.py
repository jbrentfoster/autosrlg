import json
import logging
import collectioncode.utils as utils
import xml.dom.minidom
import xml.parsers.expat
import random


def parse_ssrgs():
    srrg_types = ["Conduit", "Node", "Degree", "Add/Drop", "Switch", "Link", "Card", "Future", "Central Office",
                  "Future", "Future", "Future", "Future", "Future", "Future", "Future"]

    with open("jsongets/SRRGs.json", 'rb') as f:
        srrgs = json.load(f)
        f.close()

    for srrg in srrgs['com.response-message']['com.data']['srrg.srrg-attributes']:
        fdn = srrg['srrg.fdn']
        srrg_val = fdn.split('!')[1].split('=')[1]
        srrg['srrg-dec'] = srrg_val
        srrg['srrg-hex'] = "0x{:08x}".format(int(srrg_val))
        srrg['srrg-bin'] = "{:032b}".format(int(srrg_val))
        srrg['user-set'] = srrg['srrg-bin'][2] == '1'
        srrg['region-bin'] = srrg['srrg-bin'][3:8]
        srrg['region-dec'] = int(srrg['srrg-bin'][3:8], 2)
        srrg['type-bin'] = srrg['srrg-bin'][8:12]
        srrg['type-dec'] = int(srrg['srrg-bin'][8:12], 2)
        srrg['type-string'] = srrg_types[int(srrg['type-dec'])]
        srrg['value-bin'] = srrg['srrg-bin'][12:32]
        srrg['value-dec'] = int(srrg['srrg-bin'][12:32], 2)

    with open("jsonfiles/SRRG_db.json", 'w', encoding="utf8") as f:
        # f.write(json.dumps(srrgs, f, sort_keys=True, indent=4, separators=(',', ': ')))
        json.dump(srrgs, f, sort_keys=True, indent=4, separators=(',', ': '))
        f.close()


def processl1nodes(region, type):
    with open("jsonfiles/l1-nodes_db.json", 'rb') as f:
        l1nodes = json.load(f)
        f.close()

    for k1, v1 in l1nodes.items():
        logging.info("")
        logging.info("Matching node " + v1['Name'])
        matched_srrgs = getNodeSRRGs(v1['Name'])
        srrg_list = []
        wrong_srrg_list = []
        if len(matched_srrgs) > 0:
            logging.info("Matched an SRRG...")
            for srrg in matched_srrgs:
                logging.info(srrg['srrg.fdn'])
                logging.info("Region is: " + str(srrg['region-dec']))
                logging.info("Type is: " + srrg['type-string'])
                if srrg['region-dec'] == region and srrg['type-string'] == type:
                    logging.info("Region & type matches, node db updated.")
                    srrg_list.append(srrg['srrg.fdn'])
                else:
                    logging.info("Region and/or type doesn't match!")
                    wrong_srrg_list.append(srrg['srrg.fdn'])
        v1['srrgs'] = srrg_list
        v1['srrgs-incorrect'] = wrong_srrg_list

    with open("jsonfiles/l1-nodes_db.json", 'w', encoding="utf8") as f:
        # f.write(json.dumps(l1nodes, f, sort_keys=True, indent=4, separators=(',', ': ')))
        json.dump(l1nodes, f, sort_keys=True, indent=4, separators=(',', ': '))
        f.close()


def generatel1node_srrgs(baseURL, epnmuser, epnmpassword, pool):
    with open("jsonfiles/l1-nodes_db.json", 'rb') as f:
        l1nodes = json.load(f)
        f.close()

    for k1, v1 in l1nodes.items():
        logging.info("")
        logging.info("Generating SRRGs for node: " + v1['Name'])
        if len(v1['srrgs']) > 0:
            logging.info("Node already has SRRG: ")
            logging.info(v1['srrgs'])
        elif len(v1['srrgs']) > 1:
            logging.info("Node has more than one SRRG: ")
            logging.info(v1['srrgs'])
        else:
            usrlabel = v1['Name'] + "-" + str(random.randint(1, 1001))
            description = "Automated by Python."
            respool = pool
            rsfdn = "<p:resource-fdn>" + v1['fdn'] + "</p:resource-fdn>"
            createSRRG(baseURL, epnmuser, epnmpassword, usrlabel, description, respool, rsfdn)


def unassignl1node_srrgs(baseURL, epnmuser, epnmpassword, srrg_type):
    # srrg_type should be either 'srrgs' or srrgs-incorrect
    with open("jsonfiles/l1-nodes_db.json", 'rb') as f:
        l1nodes = json.load(f)
        f.close()

    for k1, v1 in l1nodes.items():
        logging.info("")
        logging.info("Unassigning SRRGs for node: " + v1['Name'])
        if len(v1[srrg_type]) == 0:
            logging.info("Node has no SRRGs")
        else:
            for srrg in v1[srrg_type]:
                fdn = srrg
                rsfdn = v1['fdn']
                unassignSRRG(baseURL, epnmuser, epnmpassword, fdn, rsfdn)


def getNodeSRRGs(nodename):
    with open("jsonfiles/SRRG_db.json", 'rb') as f:
        srrgs = json.load(f)
        f.close()
    matched_srrgs = []
    for srrg in srrgs['com.response-message']['com.data']['srrg.srrg-attributes']:
        fdn = srrg['srrg.fdn']
        srrgrsdict = srrg['srrg.resource-list']
        if isinstance(srrgrsdict, dict):
            srrgrslist = srrgrsdict['srrg.resource']
            if isinstance(srrgrslist, list):
                for srrgrs in srrgrslist:
                    rsfdn = srrgrs['srrg.resource-fdn']
                    srrgrs_type = rsfdn.split('!')[1].split('=')[0]
                    if srrgrs_type == "ND":
                        node = rsfdn.split('!')[1].split('=')[1]
                        if node == nodename:
                            matched_srrgs.append(srrg)
            elif isinstance(srrgrslist, dict):
                rsfdn = srrgrslist['srrg.resource-fdn']
                srrgrs_type = rsfdn.split('!')[1].split('=')[0]
                if srrgrs_type == "ND":
                    node = rsfdn.split('!')[1].split('=')[1]
                    if node == nodename:
                        matched_srrgs.append(srrg)
    return matched_srrgs


def processl1links(region, type):
    with open("jsonfiles/l1-links_db.json", 'rb') as f:
        l1links = json.load(f)
        f.close()

    for k1, v1 in l1links.items():
        logging.info("")
        logging.info("Matching L1 link " + v1['fdn'])
        matched_srrgs = getLinkSRRGs(v1['fdn'])
        srrg_list = []
        wrong_srrg_list = []
        conduit_srrg_list = []
        if len(matched_srrgs) > 0:
            logging.info("Matched an SRRG...")
            for srrg in matched_srrgs:
                logging.info(srrg['srrg.fdn'])
                logging.info("Region is: " + str(srrg['region-dec']))
                logging.info("Type is: " + srrg['type-string'])
                if srrg['region-dec'] == region and srrg['type-string'] == type:
                    logging.info("Region & ROADM degree type matches, link db updated.")
                    srrg_list.append(srrg['srrg.fdn'])
                elif srrg['region-dec'] == region and srrg['type-string'] == 'Conduit':
                    logging.info("Region & conduit type matches, link db updated.")
                    conduit_srrg_list.append(srrg['srrg.fdn'])
                else:
                    logging.info("Region and/or type doesn't match!")
                    wrong_srrg_list.append(srrg['srrg.fdn'])
        v1['srrgs'] = srrg_list
        v1['srrgs-incorrect'] = wrong_srrg_list
        v1['srrgs-conduit'] = conduit_srrg_list

    with open("jsonfiles/l1-links_db.json", 'w', encoding="utf8") as f:
        # f.write(json.dumps(l1links, f, sort_keys=True, indent=4, separators=(',', ': ')))
        json.dump(l1links, f, sort_keys=True, indent=4, separators=(',', ': '))
        f.close()


def getLinkSRRGs(linkfdn):
    with open("jsonfiles/SRRG_db.json", 'rb') as f:
        srrgs = json.load(f)
        f.close()
    matched_srrgs = []
    for srrg in srrgs['com.response-message']['com.data']['srrg.srrg-attributes']:
        fdn = srrg['srrg.fdn']
        srrgrsdict = srrg['srrg.resource-list']
        if isinstance(srrgrsdict, dict):
            srrgrslist = srrgrsdict['srrg.resource']
            if isinstance(srrgrslist, list):
                for srrgrs in srrgrslist:
                    rsfdn = srrgrs['srrg.resource-fdn']
                    srrgrs_type = rsfdn.split('!')[1].split('=')[0]
                    if srrgrs_type == "TL":
                        link = rsfdn.split('!')[1].split('=')[1]
                        if rsfdn == linkfdn:
                            matched_srrgs.append(srrg)
            elif isinstance(srrgrslist, dict):
                rsfdn = srrgrslist['srrg.resource-fdn']
                srrgrs_type = rsfdn.split('!')[1].split('=')[0]
                if srrgrs_type == "TL":
                    link = rsfdn.split('!')[1].split('=')[1]
                    if rsfdn == linkfdn:
                        matched_srrgs.append(srrg)
    return matched_srrgs


def generatel1link_srrgs(baseURL, epnmuser, epnmpassword, pool):
    with open("jsonfiles/l1-links_db.json", 'rb') as f:
        l1links = json.load(f)
        f.close()

    for k1, v1 in l1links.items():
        logging.info("")
        logging.info("Generating SRRGs for link: " + v1['fdn'])
        if len(v1['srrgs']) > 0:
            logging.info("Link already has SRRG(s): ")
            logging.info(v1['srrgs'])
        elif len(v1['srrgs']) > 1:
            logging.info("Node has more than one SRRG: ")
            logging.info(v1['srrgs'])
        else:
            usrlabel = "Link SRRG - " + str(random.randint(1, 10001))
            description = "Automated by Python."
            respool = pool
            rsfdn = "<p:resource-fdn>" + v1['fdn'] + "</p:resource-fdn>"
            createSRRG(baseURL, epnmuser, epnmpassword, usrlabel, description, respool, rsfdn)


def assignl1link_srrg(baseURL, epnmuser, epnmpassword, pool, link_fdn_list):
    usrlabel = "Conduit SRRG - " + str(random.randint(1, 10001))
    description = "Automated by Python."
    respool = pool
    xml_fdn_list = ""
    for fdn in link_fdn_list:
        xml_fdn_list += "<p:resource-fdn>" + fdn + "</p:resource-fdn>" + "\n"
    createSRRG(baseURL, epnmuser, epnmpassword, usrlabel, description, respool, xml_fdn_list)


def unassignl1link_srrgs(baseURL, epnmuser, epnmpassword, srrg_type):
    # srrg_type should be either 'srrgs' or srrgs-incorrect
    with open("jsonfiles/l1-links_db.json", 'rb') as f:
        l1links = json.load(f)
        f.close()

    for k1, v1 in l1links.items():
        logging.info("")
        logging.info("Unassigning SRRGs for link: " + v1['fdn'])
        if len(v1[srrg_type]) == 0:
            logging.info("Link has no SRRGs")
        else:
            for srrg in v1[srrg_type]:
                fdn = srrg
                rsfdn = v1['fdn']
                unassignSRRG(baseURL, epnmuser, epnmpassword, fdn, rsfdn)


def unassign_single_l1link_srrgs(baseURL, epnmuser, epnmpassword, link_fdn, srrg_type):
    # srrg_type should be either 'srrgs' or srrgs-incorrect
    with open("jsonfiles/l1-links_db.json", 'rb') as f:
        l1links = json.load(f)
        f.close()
    logging.info("Unassigning SRRGs for link: " + link_fdn)
    for k1, v1 in l1links.items():
        if v1['fdn'] == link_fdn:
            if len(v1[srrg_type]) == 0:
                logging.info("Link has no SRRGs")
            else:
                for srrg in v1[srrg_type]:
                    fdn = srrg
                    rsfdn = v1['fdn']
                    unassignSRRG(baseURL, epnmuser, epnmpassword, fdn, rsfdn)

def unassigntopolink_srrgs(baseURL, epnmuser, epnmpassword, srrg_type):
    # srrg_type should be either 'srrgs' or srrgs-incorrect
    with open("jsonfiles/topolinks_add_drop_db.json", 'rb') as f:
        topolinks = json.load(f)
        f.close()

    for k1, v1 in topolinks.items():
        logging.info("")
        logging.info("Unassigning SRRGs for link: " + v1['fdn'])
        if len(v1[srrg_type]) == 0:
            logging.info("Link has no SRRGs")
        else:
            for srrg in v1[srrg_type]:
                fdn = srrg
                rsfdn = v1['fdn']
                unassignSRRG(baseURL, epnmuser, epnmpassword, fdn, rsfdn)


def processtopolinks(region):
    with open("jsonfiles/topolinks_add_drop_db.json", 'rb') as f:
        topolinks = json.load(f)
        f.close()

    for k1, v1 in topolinks.items():
        logging.info("")
        logging.info("Matching topo link " + v1['fdn'])
        matched_srrgs = getLinkSRRGs(v1['fdn'])
        srrg_lc_list = []
        srrg_ad_list = []
        wrong_srrg_list = []
        if len(matched_srrgs) > 0:
            logging.info("Matched an SRRG...")
            for srrg in matched_srrgs:
                logging.info(srrg['srrg.fdn'])
                logging.info("Region is: " + str(srrg['region-dec']))
                logging.info("Type is: " + srrg['type-string'])
                if srrg['region-dec'] == region and srrg['type-string'] == 'Add/Drop':
                    logging.info("Region & type matches, link db updated.")
                    srrg_ad_list.append(srrg['srrg.fdn'])
                elif srrg['region-dec'] == region and srrg['type-string'] == 'Card':
                    logging.info("Region & type matches, link db updated.")
                    srrg_lc_list.append(srrg['srrg.fdn'])
                else:
                    logging.info("Region and/or type doesn't match!")
                    wrong_srrg_list.append(srrg['srrg.fdn'])
        v1['srrgs-lc'] = srrg_lc_list
        v1['srrgs-ad'] = srrg_ad_list
        v1['srrgs-incorrect'] = wrong_srrg_list

    with open("jsonfiles/topolinks_add_drop_db.json", 'w', encoding="utf8") as f:
        # f.write(json.dumps(topolinks, f, sort_keys=True, indent=4, separators=(',', ': ')))
        json.dump(topolinks, f, sort_keys=True, indent=4, separators=(',', ': '))
        f.close()


def generatetopolink_add_drop_srrgs(baseURL, epnmuser, epnmpassword, pool):
    with open("jsonfiles/l1-nodes_db.json", 'rb') as f:
        l1nodes = json.load(f)
        f.close()

    for k1, v1 in l1nodes.items():
        logging.info("")
        logging.info("Evaluating topolinks for node: " + v1['Name'])
        # if v1['Name'] == "NCS2K-Site2":
        #     continue
        fdn_a_list = []
        fdn_b_list = []
        with open("jsonfiles/topolinks_add_drop_db.json", 'rb') as f:
            topolinks = json.load(f)
            f.close()
            for key1, val1 in topolinks.items():
                for node in val1['Nodes']:
                    if node['node'] == v1['Name']:
                        logging.info('Checking topo link ' + val1['fdn'])
                        if len(val1['srrgs-ad']) > 0:
                            logging.info('Topo link already has correct SRRG assignment')
                        else:
                            ctp = node['ctp'].split('-')[0] + "-" + node['ctp'].split('-')[1] + "-" + \
                                  node['ctp'].split('-')[2]
                            if ctp == "PSLINE-81-1":
                                fdn_a_list.append({ctp: val1['fdn']})
                            elif ctp == "PSLINE-81-2":
                                fdn_b_list.append({ctp: val1['fdn']})
        if len(fdn_a_list) > 0:
            print ("Topo links for PSLINE-81-1")
            xml_fdn_list = ""
            for fdn in fdn_a_list:
                xml_fdn_list += "<p:resource-fdn>" + fdn['PSLINE-81-1'] + "</p:resource-fdn>" + "\n"
            print (xml_fdn_list)
            usrlabel = "Add/Drop Node " + v1['Name'] + "  PSLINE-81-1-" + str(random.randint(1, 10001))
            description = "Automated by Python."
            respool = pool
            createSRRG(baseURL, epnmuser, epnmpassword, usrlabel, description, respool, xml_fdn_list)

            # raw_input("Press ENTER to continue...")

        if len(fdn_b_list) > 0:
            print ("Topo links for PSLINE-81-2")
            xml_fdn_list = ""
            for fdn in fdn_b_list:
                xml_fdn_list += "<p:resource-fdn>" + fdn['PSLINE-81-2'] + "</p:resource-fdn>" + "\n"
            print (xml_fdn_list)
            usrlabel = "Add/Drop Node " + v1['Name'] + "  PSLINE-81-2-" + str(random.randint(1, 10001))
            description = "Automated by Python."
            respool = pool
            createSRRG(baseURL, epnmuser, epnmpassword, usrlabel, description, respool, xml_fdn_list)

            # raw_input("Press ENTER to continue...")


def generatetopolink_line_card_srrgs(baseURL, epnmuser, epnmpassword, pool):
    with open("jsonfiles/4k-nodes_db.json", 'rb') as f:
        l1nodes = json.load(f)
        f.close()

    for k1, v1 in l1nodes.items():
        logging.info("")
        logging.info("Evaluating topolinks for node: " + v1['Name'])
        # if v1['Name'] == "NCS2K-Site2":
        #     continue
        fdn_a_list = []
        fdn_b_list = []
        with open("jsonfiles/topolinks_add_drop_db.json", 'rb') as f:
            topolinks = json.load(f)
            f.close()
            for key1, val1 in topolinks.items():
                for node in val1['Nodes']:
                    if node['node'] == v1['Name']:
                        logging.info('Checking topo link ' + val1['fdn'])
                        if len(val1['srrgs-lc']) > 0:
                            logging.info('Topo link already has correct SRRG assignment')
                        else:
                            logging.info('Topo link requires SRRG assignment')
                            usrlabel = "Line Card Node " + v1['Name'] + " " + node['ctp'] + str(
                                random.randint(1, 10001))
                            description = "Automated by Python."
                            respool = pool
                            rsfdn = "<p:resource-fdn>" + val1['fdn'] + "</p:resource-fdn>"
                            createSRRG(baseURL, epnmuser, epnmpassword, usrlabel, description, respool, rsfdn)
                        # raw_input("Press ENTER to continue...")


def deleteSRRG(baseURL, epnmuser, epnmpassword, fdn, rsfdn):
    with open("collectioncode/post-srrg.xml", 'r') as f:
        xmlbody = f.read()
        f.close()
    logging.info("Attempting to delete SRRG: " + fdn)
    newxmlbody = xmlbody.format(fdn=fdn, rsfdn=rsfdn)
    uri = "/operations/v1/cisco-resource-activation:delete-shared-risk-resource-group"
    xmlresponse = utils.rest_post_xml(baseURL, uri, newxmlbody, epnmuser, epnmpassword)

    try:
        thexml = xml.dom.minidom.parseString(xmlresponse)
    except xml.parsers.expat.ExpatError as err:
        logging.info("XML parsing error.  The received message from websocket is not XML.")
        return
    except Exception as err:
        logging.warn("Operation failed.")
        return

    result = thexml.getElementsByTagName("ns19:status")[0].firstChild.nodeValue
    fdn = thexml.getElementsByTagName("ns19:fdn")[0].firstChild.nodeValue
    logging.info(fdn)
    logging.info(result)


def unassignSRRG(baseURL, epnmuser, epnmpassword, fdn, rsfdn):
    with open("collectioncode/post-srrg.xml", 'r') as f:
        xmlbody = f.read()
        f.close()
    logging.info("Attempting to delete SRRG: " + fdn)
    newxmlbody = xmlbody.format(fdn=fdn, rsfdn=rsfdn)
    logging.info (newxmlbody)
    uri = "/operations/v1/cisco-resource-activation:unassign-shared-risk-resource-group"
    xmlresponse = utils.rest_post_xml(baseURL, uri, newxmlbody, epnmuser, epnmpassword)

    # print xmlresponse
    try:
        thexml = xml.dom.minidom.parseString(xmlresponse)
    except xml.parsers.expat.ExpatError as err:
        logging.info("XML parsing error.  The received message from websocket is not XML.")
        return
    except Exception as err:
        logging.warning (xmlresponse)
        logging.warning("Operation failed.")
        return

    result = thexml.getElementsByTagName("ns19:status")[0].firstChild.nodeValue
    fdn = thexml.getElementsByTagName("ns19:fdn")[0].firstChild.nodeValue
    logging.info(fdn)
    logging.info(result)


def createSRRG(baseURL, epnmuser, epnmpassword, usrlabel, description, respool, rsfdn):
    with open("collectioncode/create-srrg.xml", 'r') as f:
        xmlbody = f.read()
        f.close()
        logging.info("Attempting to create SRRG...")

    uri = "/operations/v1/cisco-resource-activation:create-shared-risk-resource-group"
    newxmlbody = xmlbody.format(usrlabel=usrlabel, description=description, respool=respool, rsfdn=rsfdn)
    logging.info(newxmlbody)
    xmlresponse = utils.rest_post_xml(baseURL, uri, newxmlbody, epnmuser, epnmpassword)

    try:
        thexml = xml.dom.minidom.parseString(xmlresponse)
    except xml.parsers.expat.ExpatError as err:
        logging.warning("XML parsing error.  The received message from websocket is not XML.")
        return
    except Exception as err:
        logging.warning("Operation failed.")
        return

    try:
        result = thexml.getElementsByTagName("ns19:status")[0].firstChild.nodeValue
        fdn = thexml.getElementsByTagName("ns19:fdn")[0].firstChild.nodeValue
        logging.info("EPNM generated SRRG: " + fdn)
        logging.info("Result: " + result)
    except Exception as err:
        logging.warning("Error parsing response")
        logging.warning(xmlresponse)
