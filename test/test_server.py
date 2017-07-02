from contextlib import contextmanager
import json
import shutil
import tempfile

import pytest


import sys
import os
sys.path.append(os.path.dirname(__file__))
import testdata

_HEADERS = {
    "Content-type": "application/json",
    "Accept": ["application/json"]
}


@pytest.fixture
def client(db_with_test_data):
    return db_with_test_data["app"].test_client()

def test_slshosts(client):
    payload = { "url": testdata.SLS_BOOTSTRAP_URL }
    rv = client.post(
        "/slshosts",
        data=json.dumps(payload),
        headers=_HEADERS)

    assert rv.status_code == 200

    response = json.loads(rv.data)
    assert len(response) > 0  # TODO: a better test on the response


def test_archive_participants(client):
    payload = { "url": testdata.ESMOND_BASE_URL }
    rv = client.post(
        "/esmond/participants",
        data=json.dumps(payload),
        headers=_HEADERS)

    assert rv.status_code == 200

    response = json.loads(rv.data)
    assert len(response) > 0  # TODO: a better test on the response
