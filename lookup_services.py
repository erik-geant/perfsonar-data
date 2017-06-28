import requests
import logging


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


def _load_hosts(url):

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

    host_map = {}
    for h in _service_elements_by_type(service_data, "host"):
        assert "uri" in h
        host_map[h["uri"]] = h

    for s in _service_elements_by_type(service_data, "service"):
        if "service-host" not in s or len(s["service-host"]) == 0:
            logging.debug("no service-host for: " + str(s))
            continue
        service_host = s["service-host"][0]
        if service_host not in host_map.keys():
            logging.debug("host not found for: " + str(s))
            continue
        h = host_map[service_host]
        host_services = h.get("services", [])
        host_services.append(s)

    return host_map.values()


if __name__ == "__main__":

    logging.basicConfig(level=logging.WARN)

    SLS_BOOTSTRAP_URL = "http://ps-west.es.net:8096/lookup/activehosts.json"

    for mirror_url in _load_sls_mirrors(SLS_BOOTSTRAP_URL):
        hosts = list(_load_hosts(mirror_url))
        print "%s hosts: %d" % (mirror_url, len(hosts))



# print list(_load_sls_mirrors())
