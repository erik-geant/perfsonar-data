import json

from flask import request, Response
from werkzeug.exceptions import BadRequest

from perfsonar_data.app import app, db
from perfsonar_data import sls, esmond

_DEFAULT_SLS_BOOTSTRAP_URL = "http://ps-west.es.net:8096/lookup/activehosts.json"

def _lookup_host_element_to_response_element(host):
    """
    convert an element in the list returned by sls.download_lookup_data
    to an element of the list to be returned from /slshosts

    :param host:
    :return:
    """
    element = {}
    if len(host["host"]) > 0:
        element["host-name"] = host["host"][0].get("host-name", [])
    else:
        element["host-name"] = []

    if len(host["psmetadata"]) > 0:
        element["psmetadata-ma-locator"] = \
            host["psmetadata"][0].get("psmetadata-ma-locator", [])
    else:
        element["psmetadata-ma-locator"] = []

    if len(host["service"]) > 0:
        element["location"] = sls.get_service_location(host["service"][0])
    else:
        element["location"] = None

    return element


@app.route("/slshosts", methods=["POST"])
def slshosts():

    if not request.accept_mimetypes.accept_json:
        return Response(
            response="response will be json",
            status=406,
            mimetype="text/html")

    parsed_request = request.get_json()
    if parsed_request is  None:
        url = _DEFAULT_SLS_BOOTSTRAP_URL
    else:
        url = parsed_request.get("url", _DEFAULT_SLS_BOOTSTRAP_URL)

    response = [_lookup_host_element_to_response_element(h)
        for h in sls.download_lookup_data(url, db.session)]

    return Response(json.dumps(response), mimetype="application/json")


def _grouped_participant_tests_element_to_response_element(e):
    r = e["participants"]
    r["summaries"] = []
    for t in e["tests"]:
        for event_type in t.get("event-types", []):
            for summary in event_type.get("summaries", []):
                r["summaries"].append({
                    "ref": summary["uri"].replace("/esmond/perfsonar/archive/", ""),
                    "time": summary["time-updated"],
                    "type": event_type["event-type"],
                    "window": summary["summary-window"],
                })
    return r


@app.route("/esmond/participants", methods=["POST"])
def esmond_participants():

    if not request.accept_mimetypes.accept_json:
        return Response(
            response="response will be json",
            status=406,
            mimetype="text/html")

    parsed_request = request.get_json()
    if parsed_request is None \
            or "url" not in parsed_request \
            or not isinstance(parsed_request["url"], str):
        raise BadRequest("error reading 'url' from JSON request")

    # participants = esmond.get_test_participants(esmond.load_tests(parsed_request["url"]))
    all_tests = esmond.load_tests(parsed_request["url"], db.session)

    response = [_grouped_participant_tests_element_to_response_element(g)
                for g in esmond.group_by_participants(all_tests)]

    return Response(json.dumps(response), mimetype="application/json")


def main(port):
    app.run(
        host="0.0.0.0",
        port=port)


if __name__ == "__main__":
    # TODO: take dsn & port from cmd line
    main(8234)
