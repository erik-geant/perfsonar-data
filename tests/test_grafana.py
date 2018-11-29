import json
import logging

import pytest

from jsonschema import validate

_HEADERS = {
    "Content-type": "application/json",
    "Accept": ["application/json"]
}

MP_HOSTNAME = "64.106.40.252"

logging.basicConfig(level=logging.INFO)


def test_get_grafana_api_version(client):
    """
    sanity test on /grafana/version

    :param client: client connected to flask app with test db
    """
    rv = client.get("/grafana/version")
    assert rv.status_code == 200
    assert rv.data == b'0.1'


def test_get_grafana_metrics(client):
    """
    sanity test on /grafana/metrics

    test data contains non-zero number of metrics
    :param client: client connected to flask app with test db
    """

    payload = {
        "hostname": "64.106.40.252"
    }

    rv = client.post(
        "/grafana/metrics",
        data=json.dumps(payload),
        headers=_HEADERS)

    assert rv.status_code == 200

    response = json.loads(rv.data)

    response_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "value": {"type": "string"}
            },
            "require": ["text", "value"],
            "additionalProperties": False
        }
    }

    assert len(response) > 0  # TODO: a better test on the response
    validate(response, response_schema)
    assert len(response) > 0, "test data contains at least 1 metric"


def test_get_grafana_timeseries(client):
    """
    sanity test on /grafana/timeseries

    test data contains non-zero number of data points
    :param client: client connected to flask app with test db
    """

    payload = {
        "hostname": "64.106.40.252",
        "tsurl": "/esmond/perfsonar/archive/38db04b7baf04ff5aa26af689b33fd4d/packet-count-lost/aggregations/86400"  # noqa: ignore=E501
    }

    rv = client.post(
        "/grafana/timeseries",
        data=json.dumps(payload),
        headers=_HEADERS)

    assert rv.status_code == 200

    response = json.loads(rv.data)

    response_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "array",
        "items": {
            "type": "array",
            "items": [
                {"type": "number"},
                {"type": "number"}
            ]
        }
    }

    assert len(response) > 0  # TODO: a better test on the response
    validate(response, response_schema)
    assert len(response) > 0, "test data contains at least 1 data point"


def _get_summaries(client, measurement_type, metadata_key):

    payload = {
        "hostname": MP_HOSTNAME,
        "measurement-type": measurement_type,
        "metadata-key": metadata_key
    }

    rv = client.post(
        "/grafana/summaries",
        data=json.dumps(payload),
        headers=_HEADERS)

    assert rv.status_code == 200

    response = json.loads(rv.data)

    response_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "type": {"type": "string"},
                "window": {"type": "string"},
                "uri": {"type": "string"}
            },
            "require": ["type", "window", "uri"],
            "additionalProperties": False
        }
    }

    validate(response, response_schema)

    # TODO: a better test on the response
    assert len(response) > 0, "test data contains at least 1 data point"


def _get_participants(client, measurement_type):

    payload = {
        "hostname": MP_HOSTNAME,
        "measurement-type": measurement_type
    }

    rv = client.post(
        "/grafana/participants",
        data=json.dumps(payload),
        headers=_HEADERS)

    assert rv.status_code == 200

    response = json.loads(rv.data)

    response_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "source": {"type": "string"},
                "destination": {"type": "string"},
                "metadata-key": {"type": "string"},
                "time-updated": {"type": "integer"}
            },
            "require": ["source", "destination", "metadata-key"],
            "additionalProperties": False
        }
    }

    validate(response, response_schema)

    # TODO: a better test on the response
    assert len(response) > 0, "test data contains at least 1 data point"

    for p in response:
        _get_summaries(client, measurement_type, p["metadata-key"])


def test_all_metrics(client):
    """
    sanity test on /grafana/measurement-types,
    /grafana/participants and /grafana/summaries

    test data contains nont-zero number of data points
    :param client: client connected to flask app with test db
    """

    payload = {"hostname": MP_HOSTNAME}

    rv = client.post(
        "/grafana/measurement-types",
        data=json.dumps(payload),
        headers=_HEADERS)

    assert rv.status_code == 200

    response = json.loads(rv.data)

    response_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "array",
        "items": {"type": "string"}
    }

    validate(response, response_schema)

    # TODO: a better test on the response
    assert len(response) > 0, "test data contains at least 1 data point"

    for mt in response:
        _get_participants(client, mt)


def test_metric_types(client):

    rv = client.post(
        "/grafana/metric-types",
        headers=_HEADERS)

    assert rv.status_code == 200

    response = json.loads(rv.data)

    response_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "array",
        "items": {"type": "string"}
    }

    assert len(response) > 0  # TODO: a better test on the response
    validate(response, response_schema)
    assert len(response) > 0, "test data contains at least 1 data point"
