import logging
from perfsonar_data import proxy


def _load_sls_mirrors(url):
    """
    load url's of hosts containing ps service lists

    :param url:
    :return:
    """
    hosts = proxy.load_url_json(url)
    assert "hosts" in hosts
    for h in hosts["hosts"]:
        assert {"locator", "priority", "status"} <= set(h.keys())
        if h["status"] == "alive":
            yield h["locator"]


def _service_elements_by_type(service_data, type):
    return [e for e in service_data if type in e["type"]]


def _download_parse_lookup_data(url):
    """
    download and parse service data

    result is a list of dicts of all services with the same client-uuid,
    each element of which is formatted as:

        "hosts": list of elements of type "host" with the same client-uuid
        "service": list of elements of type "service" with the same client-uuid
        "psmetadata": list of elements of type "psmetadata" with the same client-uuid

    :param url:
    :return:
    """
    service_data = proxy.load_url_json(url)
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


def get_service_location(service_element):
    """
    utility for generating a well-formatted dict of location elements
    for a particular service_element
    :param service_element:
    :return:
    """
    location = {}
    location["city"] = service_element.get("location-city", [None])[0]
    location["country"] = service_element.get("location-country", [None])[0]
    location["latitude"] = service_element.get("location-latitude", [None])[0]
    location["longitude"] = service_element.get("location-longitude", [None])[0]
    location["sitename"] = service_element.get("location-sitename", [None])[0]
    return location


def download_lookup_data(sls_bootstrap_url):
    """
    download mirror hosts from the bootstrap url, and then for each
    download and parse the service list

    :param sls_bootstrap_url:
    :return: list of all hosts discovered on each mirror listed by the bootstrap url
    """
    hosts = []
    for mirror_url in _load_sls_mirrors(sls_bootstrap_url):
        mirror_hosts = _download_parse_lookup_data(mirror_url)
        logging.debug("downloaded from %s: %d" % (mirror_url, len(mirror_hosts)))
        hosts.extend(mirror_hosts)
    return hosts
    # print "%s clients: %d" % (mirror_url, len(clients))
    # for c in clients:
    #     for s in c["service"]:
    #         location = _get_service_location(s)
    #         logging.warn(str(location))
