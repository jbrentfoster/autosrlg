import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import json
import collectioncode.errors as errors
import xml.dom.minidom
import logging

urllib3.disable_warnings(InsecureRequestWarning)


def rest_get_json(baseURL, uri, user, password):
    proxies = {
        "http": None,
        "https": None,
    }
    appformat = 'application/json'
    headers = {'content-type': appformat, 'accept': appformat}
    restURI = baseURL + uri
    logging.info(restURI)
    try:
        r = requests.get(restURI, headers=headers, proxies=proxies, auth=(user, password), verify=False)
        # print "HTTP response code is: " + str(r.status_code)
        if r.status_code == 200:
            return json.dumps(r.json(), indent=2)
        else:
            raise errors.InputError(restURI, "HTTP status code: " + str(r.status_code))
    except errors.InputError as err:
        logging.error("Exception raised: " + str(type(err)))
        logging.error(err.expression)
        logging.error(err.message)
        return


def rest_get_xml(baseURL, uri, user, password):
    proxies = {
        "http": None,
        "https": None,
    }
    appformat = 'application/xml'
    headers = {'content-type': appformat, 'accept': appformat}
    restURI = baseURL + uri
    logging.info(restURI)
    try:
        r = requests.get(restURI, headers=headers, proxies=proxies, auth=(user, password), verify=False)
        # print "HTTP response code is: " + str(r.status_code)
        if r.status_code == 200:
            response_xml = xml.dom.minidom.parseString(r.content)
            return response_xml.toprettyxml()
        else:
            raise errors.InputError(restURI, "HTTP status code: " + str(r.status_code))
    except errors.InputError as err:
        logging.error("Exception raised: " + str(type(err)))
        logging.error(err.expression)
        logging.error(err.message)
        return


def rest_post_xml(baseURL, uri, thexml, user, password):
    proxies = {
        "http": None,
        "https": None,
    }
    appformat = 'application/xml'
    headers = {'content-type': appformat, 'accept': appformat}
    restURI = baseURL + uri
    logging.info(restURI)
    try:
        r = requests.post(restURI, data=thexml, headers=headers, proxies=proxies, auth=(user, password), verify=False)
        logging.info("HTTP response code is: " + str(r.status_code))
        if r.status_code == 200:
            response_xml = xml.dom.minidom.parseString(r.content)
            return response_xml.toprettyxml()
        else:
            logging.warning("Failed XML post!")
            logging.warning("HTTP status code: " + str(r.status_code))
            response_xml = xml.dom.minidom.parseString(r.content)
            return response_xml.toprettyxml()
            # raise errors.InputError(restURI, "HTTP status code: " + str(r.status_code) + "\n" + r.content)
    except errors.InputError as err:
        logging.error("Exception raised: " + str(type(err)))
        logging.error(err.expression)
        logging.error(err.message)
        return

def rest_post_json(baseURL, uri, thejson, user, password):
        proxies = {
            "http": None,
            "https": None,
        }
        appformat = 'application/json'
        headers = {'content-type': appformat, 'accept': appformat}
        restURI = baseURL + uri
        logging.info(restURI)
        try:
            r = requests.post(restURI, data=thejson, headers=headers, proxies=proxies, auth=(user, password),
                              verify=False)
            # print "HTTP response code is: " + str(r.status_code)
            if r.status_code == 200:
                return json.dumps(r.json(), indent=2)
            else:
                raise errors.InputError(restURI, "HTTP status code: " + str(r.status_code))
        except errors.InputError as err:
            logging.error("Exception raised: " + str(type(err)))
            logging.error(err.expression)
            logging.error(err.message)
            return

# def cleanxml(thexml):
#     cleanedupXML = "".join([s for s in thexml.splitlines(True) if s.strip("\r\n\t")])
#     return cleanedupXML
