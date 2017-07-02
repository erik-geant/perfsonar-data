import os

import pytest

import perfsonar_data
from perfsonar_data import model

import sys
sys.path.append(os.path.dirname(__file__))
import testdata

@pytest.fixture
def empty_db():
    """
    yields a sqlalchemy session to a temporary database

    the temporary database file is deleted once context mgmt is complete

    :return: dsn (string)
    """
    import tempfile

    fd, name = tempfile.mkstemp()
    os.close(fd)

    dsn = "sqlite:///" + name  # careful: assumes linux separators
    os.environ["SQLALCHEMY_DATABASE_URI"] = dsn

    from perfsonar_data import app_factory
    import flask_migrate

    tmp_test_app = app_factory.create_app(dsn)

    with tmp_test_app.app_context():
        flask_migrate.upgrade(
            directory=os.path.join(perfsonar_data.__path__[0], "migrations"),
            revision="head")

        try:
            yield {
                "app": tmp_test_app,
                "session": app_factory.db.session
            }
        finally:
           os.unlink(name)  # don't fill the disk with tmp db files


@pytest.fixture
def db_with_test_data(empty_db):
    """
    returns a session connected to a temporary database

    :param empty_db: a sqlalchemy session object
    :return: the same session
    """


    for url, filename in testdata.TEST_DATA_FILES.items():

        if empty_db["session"].query(model.Doc) \
                .filter(model.Doc.url == url) \
                .first() is not None:
            continue


        with open(os.path.join(testdata.DATA_PATH, filename),
                  encoding="utf-8") as f:
            empty_db["session"].add(model.Doc(
                url=str(url), doc=f.read()))

            empty_db["session"].commit()

    return empty_db
