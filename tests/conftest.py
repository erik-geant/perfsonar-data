import json
import os
import tempfile

import pytest

import esmond_helper
# from esmond_helper import model

from . import data


# @pytest.fixture
# def empty_db():
#     """
#     yields a sqlalchemy session to a temporary database
#
#     the temporary database file is deleted once context mgmt is complete
#
#     :return: dsn (string)
#     """
#
#     fd, db_filename = tempfile.mkstemp()
#     os.close(fd)
#
#     fd, config_filename = tempfile.mkstemp()
#     os.close(fd)
#
#     with open(config_filename, 'w') as f:
#         # careful: assumes linux separators
#         f.write('SQLALCHEMY_DATABASE_URI = "sqlite:///%s"' % db_filename)
#
#     os.environ["SETTINGS_FILENAME"] = config_filename
#     tmp_test_app = esmond_helper.create_app()
#
#     with tmp_test_app.app_context():
#         flask_migrate.upgrade(
#             directory=os.path.join(esmond_helper.__path__[0], "migrations"),
#             revision="head")
#
#         try:
#             yield {
#                 "app": tmp_test_app,
#                 "session": esmond_helper.db.session
#             }
#         finally:
#             # don't fill the disk with tmp files ...
#             os.unlink(config_filename)
#             os.unlink(db_filename)
#

class MockedRedis(object):

    db = None

    def __init__(self, *args, **kwargs):
        if MockedRedis.db is None:

            MockedRedis.db = {}
            for url, filename in data.TEST_DATA_FILES.items():

                with open(os.path.join(data.DATA_PATH, filename), 'rb') as f:
                    content = f.read()
                    MockedRedis.db[url] = content
                    MockedRedis.db[url.encode('utf-8')] = content

    def set(self, key, value):
        MockedRedis.db[key] = value

    def get(self, key):
        return MockedRedis.db[key]

    def keys(self, *args, **kwargs):
        return list([k.encode("utf-8") for k in MockedRedis.db.keys()])


@pytest.fixture
def mocked_test_redis():
    return MockedRedis()


@pytest.fixture
def db_with_test_data(mocker):
    """
    mock redis i/o with test data

    :param mocker: mocker fixture
    :return: nothing
    """
    mocker.patch(
        'esmond_helper.proxy.redis.StrictRedis',
        MockedRedis)


@pytest.fixture
def client(db_with_test_data):

    dummy_redis_params = {
        "hostname": "xyzabc",
        "port": 9999999
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        filename = os.path.join(tmpdir, "settings.json")
        with open(filename, 'w') as f:
            f.write("REDIS_PARAMS = %s" % json.dumps(dummy_redis_params))
        os.environ["SETTINGS_FILENAME"] = filename
        with esmond_helper.create_app().test_client() as c:
            yield c
