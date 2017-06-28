import json
import logging
import os

import requests

_SLS_BOOTSTRAP_URL = "http://ps-west.es.net:8096/lookup/activehosts.json"
_DEFAULT_LOOKUP_CACHE_FILENAME = ".lookup.cache.json"


def _load_sls_mirrors(url):

    import json
    with open("activehosts.json") as f:
            hosts = json.loads(f.read())

    # r = requests.get(url)
    # assert r.status_code == 200
    # assert "application/json" in r.headers["content-type"]
    # hosts = r.json()

    assert "hosts" in hosts
    for h in hosts["hosts"]:
        assert {"locator", "priority", "status"} <= set(h.keys())
        if h["status"] == "alive":
            yield h["locator"]


def _service_elements_by_type(service_data, type):
    return [e for e in service_data if type in e["type"]]


def _download_parse_lookup_data(url):

    CACHED_RECORDS = {
        "http://ps-west.es.net:8090/lookup/records": "records.ps-west",
        "http://ps-east.es.net:8090/lookup/records": "records.ps-east",
        "http://monipe-ls.rnp.br:8090/lookup/records": "records.monipe-ls",
        "http://ps-sls.sanren.ac.za:8090/lookup/records": "records.ps-sls.sanren",
        "http://nsw-brwy-sls1.aarnet.net.au:8090/lookup/records/": "records.aarnet"
    }

    assert url in CACHED_RECORDS
    import json
    with open(CACHED_RECORDS[url]) as f:
        service_data = json.loads(f.read())

    # r = requests.get(url)
    # assert r.status_code == 200
    # assert "application/json" in r.headers["content-type"]
    # services = r.json()

    assert isinstance(service_data, (list,tuple))
    logging.debug("%s elements: %d" % (url, len(service_data)))

    clients = {}
    for e in service_data:
        etype = e["type"][0]
        if "client-uuid" not in e:
            if etype in ("host", "service", "psmetadata"):
                logging.debug("no client-uuid: '%s'" % etype)
            continue

        if etype not in ("host", "service", "psmetadata"):
            logging.debug("unhandled element type: '%s'" % etype)
            continue

        client_uuid = e["client-uuid"][0]
        if client_uuid not in clients:
            clients[client_uuid] = {
                "host": [],
                "service": [],
                "psmetadata": [],
            }

        clients[client_uuid][etype].append(e)

    return clients.values()


def _get_service_location(service_element):
    location = {}
    location["city"] = service_element.get("location-city", [None])[0]
    location["country"] = service_element.get("location-country", [None])[0]
    location["latitude"] = service_element.get("location-latitude", [None])[0]
    location["longitude"] = service_element.get("location-longitude", [None])[0]
    location["sitename"] = service_element.get("location-sitename", [None])[0]
    return location


def _download_lookup_data():
    hosts = []
    for mirror_url in _load_sls_mirrors(_SLS_BOOTSTRAP_URL):
        mirror_hosts = _download_parse_lookup_data(mirror_url)
        logging.warn("%s hosts: %d" % (mirror_url, len(mirror_hosts)))
        hosts.extend(mirror_hosts)
    return hosts
    # print "%s clients: %d" % (mirror_url, len(clients))
    # for c in clients:
    #     for s in c["service"]:
    #         location = _get_service_location(s)
    #         logging.warn(str(location))


def _load_lookup_data():
    if os.path.isfile(_DEFAULT_LOOKUP_CACHE_FILENAME):
        try:
            with open(_DEFAULT_LOOKUP_CACHE_FILENAME) as f:
                return json.loads(f.read())
        except ValueError:
            logging.warn("lookup cache is corrupt, reloading...")
            pass

    hosts = _download_lookup_data()
    with open(_DEFAULT_LOOKUP_CACHE_FILENAME, "w+") as f:
        f.write(json.dumps(hosts,
                           sort_keys=True,
                           indent=4,
                           separators = (',', ': ')))
    return hosts

if __name__ == "__main__":

    logging.basicConfig(level=logging.WARN)

    print len(_load_lookup_data())



# print list(_load_sls_mirrors())
