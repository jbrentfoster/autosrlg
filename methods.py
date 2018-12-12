"""
An entire file for you to expand. Add methods here, and the client should be
able to call them with json-rpc without any editing to the pipeline.
"""
import json

# def count(number):
#     """It counts. Duh. Note: intentionally written to break on non-ints"""
#     return int(number) + 1

def getl1nodes():
    with open("jsonfiles/l1-nodes_db.json", 'rb') as f:
        l1nodes = json.load(f)
        f.close()
    return l1nodes

def getsrlg(srlg):
    with open("jsonfiles/SRRG_db.json", 'rb') as f:
        srrgs = json.load(f)
        f.close()
    for srrg in srrgs['com.response-message']['com.data']['srrg.srrg-attributes']:
        if srrg['srrg.srrg-id'] == srlg:
            return srrg
    return None

def getl1links(home_url):
    with open("jsonfiles/l1-links_db.json", 'rb') as f:
        l1links = json.load(f)
        f.close()
    l1links_html_table = "<th>Node A</th><th>Node B</th><th>SRLG<th>"
    for k,v in l1links.items():
        srlg_parsed = v['srrgs'][0].split('=')[2]
        srlg = '<a href ="'+home_url+'/srlg/'+srlg_parsed+'">'+srlg_parsed+'</a>'
        l1links_html_table += "<tr><td>"+v['Nodes'][0]+"</td><td>"+v['Nodes'][1]+"</td><td>"+srlg+"</td></tr>"
    return l1links_html_table

def gettopolinks():
    with open("jsonfiles/topolinks_add_drop_db.json", 'rb') as f:
        topo_links = json.load(f)
        f.close()
    return json.dumps(topo_links)
