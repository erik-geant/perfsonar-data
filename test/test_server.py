from contextlib import contextmanager
import json
import shutil
import tempfile

import pytest

from perfsonar_data import server

_HEADERS = {
    "Content-type": "application/json",
    "Accept": ["application/json"]
}


@contextmanager
def tempdir():
    dir_name = tempfile.mkdtemp()
    try:
        yield dir_name
    finally:
        shutil.rmtree(dir_name, ignore_errors=True)


@pytest.fixture
def client():
    return server.app.test_client()


def test_slshosts(client, db_with_test_data):
    from perfsonar_data import proxy
    import data
    proxy.init_db_engine(db_with_test_data)

    payload = { "url": data.SLS_BOOTSTRAP_URL }
    rv = client.post(
        "/slshosts",
        data=json.dumps(payload),
        headers=_HEADERS)

    assert rv.status_code == 200

    response = json.loads(rv.data)
    assert len(response) > 0  # TODO: a better test on the response


def test_archive_participants(client, db_with_test_data):
    from perfsonar_data import proxy
    import data
    proxy.init_db_engine(db_with_test_data)

    payload = { "url": data.ESMOND_BASE_URL }
    rv = client.post(
        "/esmond/participants",
        data=json.dumps(payload),
        headers=_HEADERS)

    assert rv.status_code == 200

    response = json.loads(rv.data)
    assert len(response) > 0  # TODO: a better test on the response
