"""
app request handlers
"""
import json
from numbers import Number

from jsonschema import validate, ValidationError
from flask import request, Response, Blueprint
from werkzeug.exceptions import BadRequest

# from esmond_helper.model import db
from esmond_helper import sls, esmond, proxy
import redis

_DEFAULT_SLS_BOOTSTRAP_URL = \
    "http://ps-west.es.net:8096/lookup/activehosts.json"

server = Blueprint("psdata", __name__)

def _render_lookup_host_element_as_response_element(host):
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


@server.route("/slshosts", methods=["POST"])
def slshosts():

    if not request.accept_mimetypes.accept_json:
        return Response(
            response="response will be json",
            status=406,
            mimetype="text/html")

    parsed_request = request.get_json(silent=True)
    if parsed_request is None:
        url = _DEFAULT_SLS_BOOTSTRAP_URL
    else:
        schema = {
            "type": "object",
            "properties": {
                "url": {"type": "string"}
            }
        }
        try:
            validate(parsed_request, schema)
        except ValidationError as e:
            raise BadRequest(str(e))
        url = parsed_request.get("url", _DEFAULT_SLS_BOOTSTRAP_URL)

    response = [_render_lookup_host_element_as_response_element(h)
                for h in sls.download_lookup_data(url, proxy.db())]

    return Response(json.dumps(response), mimetype="application/json")


def _render_grouped_participant_tests_element_as_response_element(e):
    r = e["participants"]
    r["summaries"] = []
    for t in e["tests"]:
        for event_type in t.get("event-types", []):
            for summary in event_type.get("summaries", []):
                r["summaries"].append({
                    "ref": summary["uri"].replace(
                        "/esmond/perfsonar/archive/", ""),
                    "time": summary["time-updated"],
                    "type": event_type["event-type"],
                    "window": summary["summary-window"],
                })
    return r


@server.route("/esmond/participants", methods=["POST"])
def esmond_participants():

    if not request.accept_mimetypes.accept_json:
        return Response(
            response="response will be json",
            status=406,
            mimetype="text/html")

    parsed_request = request.get_json()

    schema = {
        "type": "object",
        "properties": {
            "url": {"type": "string"}
        },
        "required": ["url"]
    }

    try:
        validate(parsed_request, schema)
    except ValidationError as e:
        raise BadRequest(str(e))

    # participants = esmond.get_test_participants(
    #                   esmond.load_tests(parsed_request["url"]))
    all_tests = esmond.load_tests(parsed_request["url"], proxy.db())

    response = [
        _render_grouped_participant_tests_element_as_response_element(g)
        for g in esmond.group_by_participants(all_tests)
        ]

    return Response(json.dumps(response), mimetype="application/json")


def _render_time_series_as_response(time_series_data, keys=set()):

    result = dict([(k, []) for k in keys])
    if not result:
        result["default"] = []

    for m in time_series_data:

        assert "ts" in m

        if isinstance(m["val"], Number):
            # this means the summary is a simple list of ts/val pairs
            # we can only return a single default list
            assert "default" in result, \
                "measurement data contains no subkeys"
            result["default"].append(
                {"ts": m["ts"], "value": m["val"]})
        elif isinstance(m["val"], dict):
            # add the requested values to the reult
            assert keys <= set(m["val"].keys()), \
                "a measurement data point is missing following keys: " \
                ", ".join(keys - set(m["val"].keys()))
            for k in keys:
                assert isinstance(m["val"][k], Number), \
                    "measurement data for '%s' is not a Number" % k
                result[k].append(
                    {"ts": m["ts"], "value": m["val"][k]})
        else:
            assert False, \
                "got measurement 'val' of unexpected type '%s'" \
                % str(type(m["val"]))

    return result


@server.route("/esmond/series", methods=["POST"])
def esmond_time_series():

    if not request.accept_mimetypes.accept_json:
        return Response(
            response="response will be json",
            status=406,
            mimetype="text/html")

    parsed_request = request.get_json()

    schema = {
        "type": "object",
        "properties": {
            "url": {"type": "string"},
            "id": {"type": "string"},
            "keys": {
                "type": "array",
                "minItems": 1,
                "items": {"type": "string"}
            }
        },
        "required": ["url", "id"]
    }

    try:
        validate(parsed_request, schema)
    except ValidationError as e:
        raise BadRequest(str(e))

    time_series_doc = esmond.get_time_series(
        esmond_base_url=parsed_request["url"],
        summary_id=parsed_request["id"],
        connection=proxy.db())

    if "keys" in parsed_request:
        response = _render_time_series_as_response(
            time_series_doc, keys=set(parsed_request["keys"]))
    else:
        response = _render_time_series_as_response(time_series_doc)

    return Response(json.dumps(response), mimetype="application/json")
