import json
import logging

import pytest

from jsonschema import validate

_HEADERS = {
    "Content-type": "application/json",
    "Accept": ["application/json"]
}

logging.basicConfig(level=logging.INFO)


@pytest.fixture
def client(db_with_test_data):
    return db_with_test_data["app"].test_client()


def test_get_grafana_metrics(client):
    """
    sanity test on /grafana/metrics

    test data contains non-zero number of metrics
    :param db_with_test_data: flask app and sqlalchemy session instances
    """

    payload = {
        "hostname": "perfsonar.debrecen3.hbone.hu"
    }

    rv = client.post(
        "/grafana/metrics",
        data=json.dumps(payload),
        headers=_HEADERS)

    assert rv.status_code == 200

    response = json.loads(rv.data)

    response_schema = {
        "$schema": "http://json-schema.org/draft-04/schema#",
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
    :param db_with_test_data: flask app and sqlalchemy session instances
    """

    payload = {
        "hostname": "perfsonar.debrecen3.hbone.hu",
        "tsurl": "/esmond/perfsonar/archive/4b84bee4247e419a9b422a85b27d4f78/packet-count-lost/aggregations/86400"  # noqa: ignore=E501
    }

    rv = client.post(
        "/grafana/timeseries",
        data=json.dumps(payload),
        headers=_HEADERS)

    assert rv.status_code == 200

    response = json.loads(rv.data)

    response_schema = {
        "$schema": "http://json-schema.org/draft-04/schema#",
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
