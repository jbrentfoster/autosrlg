import json

# def count(number):
#     """It counts. Duh. Note: intentionally written to break on non-ints"""
#     return int(number) + 1

def getl1nodes():
    with open("jsonfiles/l1-nodes_db.json", 'rb') as f:
        l1nodes = json.load(f)
        f.close()
    return json.dumps(l1nodes)

def getsrlg(srlg):
    with open("jsonfiles/SRRG_db.json", 'rb') as f:
        srrgs = json.load(f)
        f.close()
    for srrg in srrgs['com.response-message']['com.data']['srrg.srrg-attributes']:
        if str(srrg['srrg.srrg-id']) == srlg:
            return json.dumps(srrg)
    return None

def getl1links():
    with open("jsonfiles/l1-links_db.json", 'rb') as f:
        l1links = json.load(f)
        f.close()
    return json.dumps(l1links)

def gettopolinks():
    with open("jsonfiles/topolinks_add_drop_db.json", 'rb') as f:
        topo_links = json.load(f)
        f.close()
    return json.dumps(topo_links)
