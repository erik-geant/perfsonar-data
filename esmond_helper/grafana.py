"""
grafana route request handlers
"""
import json
import time

from jsonschema import validate, ValidationError
from flask import request, Response, Blueprint
from werkzeug.exceptions import BadRequest

from esmond_helper.model import db
from esmond_helper import proxy
from esmond_helper import common
from esmond_helper import esmond

server = Blueprint("grafana", __name__)

_24H_SECONDS = 24 * 60 * 60
_DEFAULT_METRIC_LIST_EXPIRATION = _24H_SECONDS
_DEFAULT_TIMESERIES_REQUEST_EXPIRATION = 60
_DEFAULT_TIMESERIES_METRIC_TYPE = "mean"

_ESMOND_ARCHIVE_PATH = "/esmond/perfsonar/archive/"


@server.route("/version", methods=['GET', 'POST'])
def get_version():
    return Response("0.1")


@server.route("/metrics", methods=["POST"])
@common.require_accepts_json
def measurement_archive_metrics():

    parsed_request = request.get_json()

    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "hostname": {"type": "string"},
            "eventtypes": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": [
                        "throughput",
                        "packet-count-sent",
                        "packet-count-lost"]
                }
            },
            "cacheseconds": {
                "type": "integer",
                "minimum": 0,
                "exclusiveMinimum": True
            }
        },
        "required": ["hostname"]
    }

    try:
        validate(parsed_request, schema)
    except ValidationError as e:
        raise BadRequest(str(e))

    event_types = parsed_request.get(
        "eventtypes",
        ["throughput", "packet-count-sent", "packet-count-lost"])
    cache_seconds = parsed_request.get(
        "cacheseconds", _DEFAULT_METRIC_LIST_EXPIRATION)

    archive_json = proxy.load_url_json(
        url="http://%s/%s" % (
            parsed_request["hostname"], _ESMOND_ARCHIVE_PATH),
        session=db.session,
        expires=cache_seconds+int(time.time()))

    def _summaries():
        for m in archive_json:
            for t in m["event-types"]:
                if t["event-type"] not in event_types:
                    continue
                for s in t["summaries"]:
                    yield {
                        "text": "%s, %s [%s]" % (
                            m["destination"],
                            t["event-type"],
                            s["summary-window"]),
                        "value": s["uri"]
                    }

    return Response(
        json.dumps(list(_summaries())),
        mimetype="application/json")


@server.route("/timeseries", methods=["POST"])
@common.require_accepts_json
def measurement_archive_timeseries():

    parsed_request = request.get_json()

    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "hostname": {"type": "string"},
            "tsurl": {"type": "string"},
            "metric": {"type": "string"}
        },
        "required": ["hostname", "tsurl"]
    }

    try:
        validate(parsed_request, schema)
    except ValidationError as e:
        raise BadRequest(str(e))

    timeseries_json = proxy.load_url_json(
        url="http://%s/%s" % (
            parsed_request["hostname"], parsed_request["tsurl"]),
        session=db.session,
        expires=_DEFAULT_TIMESERIES_REQUEST_EXPIRATION + int(time.time()))

    if timeseries_json and isinstance(timeseries_json[0]["val"], dict):
        metric = parsed_request.get("metric", _DEFAULT_TIMESERIES_METRIC_TYPE)
        if metric == "mode":
            # hack ... this is just what was seen in sample queries
            datapoints = [[x["val"][metric][0], 1000 * x["ts"]] for x in timeseries_json]
        else:
            datapoints = [[x["val"][metric], 1000 * x["ts"]] for x in timeseries_json]
    else:
        datapoints = [[x["val"], 1000 * x["ts"]] for x in timeseries_json]

    return Response(
        json.dumps(list(datapoints)),
        mimetype="application/json")


@server.route("/measurement-types", methods=["POST"])
@common.require_accepts_json
def measurement_types():

    parsed_request = request.get_json()

    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "hostname": {"type": "string"},
        },
        "required": ["hostname"]
    }

    try:
        validate(parsed_request, schema)
    except ValidationError as e:
        raise BadRequest(str(e))

    return Response(
        json.dumps(
            esmond.get_available_measurement_types(
                mp_hostname=parsed_request["hostname"],
                session=db.session
            )
        ),
        mimetype="application/json"
    )


@server.route("/participants", methods=["POST"])
@common.require_accepts_json
def participants():

    parsed_request = request.get_json()

    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "hostname": {"type": "string"},
            "measurement-type": {"type": "string"}
        },
        "required": ["hostname", "measurement-type"]
    }

    try:
        validate(parsed_request, schema)
    except ValidationError as e:
        raise BadRequest(str(e))

    return Response(
        json.dumps(
            esmond.get_available_participants(
                mp_hostname=parsed_request["hostname"],
                measurement_type=parsed_request["measurement-type"],
                session=db.session
            )
        ),
        mimetype="application/json"
    )


@server.route("/summaries", methods=["POST"])
@common.require_accepts_json
def summaries():

    parsed_request = request.get_json()

    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "hostname": {"type": "string"},
            "measurement-type": {"type": "string"},
            "metadata-key": {"type": "string"}
        },
        "required": ["hostname", "measurement-type", "metadata-key"]
    }

    try:
        validate(parsed_request, schema)
    except ValidationError as e:
        raise BadRequest(str(e))

    return Response(
        json.dumps(
            esmond.get_available_summaries(
                mp_hostname=parsed_request["hostname"],
                measurement_type=parsed_request["measurement-type"],
                metadata_key=parsed_request["metadata-key"],
                session=db.session
            )
        ),
        mimetype="application/json"
    )


@server.route("/metric-types", methods=["POST"])
@common.require_accepts_json
def types():

    metric_types = [
        "standard-deviation",
        "median",
        "maximum",
        "minimum",
        "mode",
        "percentile-75",
        "percentile-25",
        "percentile-95",
        "variance",
        "mean"
    ]

    return Response(
        json.dumps(metric_types),
        mimetype="application/json")
