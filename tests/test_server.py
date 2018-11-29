import json
import pytest

from jsonschema import validate

from . import data

_HEADERS = {
    "Content-type": "application/json",
    "Accept": ["application/json"]
}


def test_slshosts(client):
    payload = {"url": data.SLS_BOOTSTRAP_URL}
    rv = client.post(
        "/slshosts",
        data=json.dumps(payload),
        headers=_HEADERS)

    assert rv.status_code == 200

    response = json.loads(rv.data)
    assert len(response) > 0  # TODO: a better test on the response


def test_archive_participants(client):
    payload = {"url": data.ESMOND_BASE_URL}
    rv = client.post(
        "/esmond/participants",
        data=json.dumps(payload),
        headers=_HEADERS)

    assert rv.status_code == 200

    response = json.loads(rv.data)
    assert len(response) > 0  # TODO: a better test on the response


def test_archive_participants_no_payload(client):
    rv = client.post(
        "/esmond/participants",
        headers=_HEADERS)

    assert rv.status_code == 400


def test_archive_participants_bad_payload(client):
    payload = {"url1": data.ESMOND_BASE_URL}
    rv = client.post(
        "/esmond/participants",
        data=json.dumps(payload),
        headers=_HEADERS)

    assert rv.status_code == 400


def _TIME_SERIES_RESPONSE_SCHEMA(keys=["default"]):
    ts_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "oneOf": [{"$ref": "#/definitions/measurementPoint"}],
            "minItems": 1
        }
    }
    return {
        "type": "object",
        "properties": dict([(k, ts_schema) for k in keys]),
        "required": keys,
        "definitions": {
            "measurementPoint": {
                "type": "object",
                "properties": {
                    "ts": {"type": "number"},
                    "value": {"type": "number"}
                },
                "required": ["ts", "value"]
            }
        }
    }


def test_time_series(client):
    payload = {
        "url": data.ESMOND_BASE_URL,
        "id": data.THROUGHPUT_ID
    }
    rv = client.post(
        "/esmond/series",
        data=json.dumps(payload),
        headers=_HEADERS)

    assert rv.status_code == 200

    response = json.loads(rv.data)
    validate(response, _TIME_SERIES_RESPONSE_SCHEMA())


def test_time_series_keys(client):
    measurement_keys = ["standard-deviation", "percentile-95", "maximum"]
    payload = {
        "url": data.ESMOND_BASE_URL,
        "id": data.OWDELAY_HISTOGRAM_ID,
        "keys": measurement_keys,
    }
    rv = client.post(
        "/esmond/series",
        data=json.dumps(payload),
        headers=_HEADERS)

    assert rv.status_code == 200

    response = json.loads(rv.data)
    validate(response, _TIME_SERIES_RESPONSE_SCHEMA(measurement_keys))
