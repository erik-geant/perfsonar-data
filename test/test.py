import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import perfsonar_data
from perfsonar_data import esmond
from perfsonar_data import proxy

import logging

logging.basicConfig(level=logging.INFO)


_ESMOND_BASE_URL = "http://158.125.250.70/"
_TEST_DATA_FILES = {
    # ACTIVE_HOSTS
    "http://ps-west.es.net:8096/lookup/activehosts.json": "activehosts.json",

    # HOST_RECORDS
    "http://ps-west.es.net:8090/lookup/records": "records.ps-west",
    "http://ps-east.es.net:8090/lookup/records": "records.ps-east",
    "http://monipe-ls.rnp.br:8090/lookup/records": "records.monipe-ls",
    "http://ps-sls.sanren.ac.za:8090/lookup/records": "records.ps-sls.sanren",
    "http://nsw-brwy-sls1.aarnet.net.au:8090/lookup/records/": "records.aarnet",

    # TEST_ARCHIVE
    _ESMOND_BASE_URL + "esmond/perfsonar/archive/": "archive.json",
}

@pytest.fixture
def esmond_base_url():
    return _ESMOND_BASE_URL

@pytest.fixture
def empty_db():
    """
    yields a dsn to a temporary database

    the temporary database file is deleted once context mgmt is complete

    :return: dsn (string)
    """
    import tempfile
    from alembic.config import Config
    from alembic import command

    fd, name = tempfile.mkstemp()
    os.close(fd)

    dsn = "sqlite:///" + name  # careful: assumes linux separators

    cfg = Config(os.path.join(perfsonar_data.__path__[0], "alembic.ini"))
    cfg.set_main_option("script_location",
                        os.path.join(perfsonar_data.__path__[0], "migrations"))
    cfg.set_main_option("sqlalchemy.url", dsn)
    command.upgrade(cfg, revision="head")

    try:
        yield dsn
    finally:
        # don't fill the disk with tmp db files
        os.unlink(name)


@pytest.fixture
def db_with_test_data(empty_db):
    """
    returns a dsn to a temporary database

    :param empty_db:
    :return: dsn (string)
    """

    engine = create_engine(empty_db)
    # engine = create_engine(empty_db, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    for url, filename in _TEST_DATA_FILES.items():

        if session.query(perfsonar_data.model.Doc) \
                .filter(perfsonar_data.model.Doc.url == url) \
                .first() is not None:
            continue

        data_path = os.path.join(os.path.dirname(__file__), "data")

        with open(os.path.join(data_path, filename)) as f:
            session.add(perfsonar_data.model.Doc(
                url=unicode(url), doc=f.read().decode("utf-8")))

        session.commit()

    session.close()
    engine.dispose()

    return empty_db


def test_testdata(db_with_test_data):
    """
    basic sanity test on the test db creation
    :param db_with_test_data: dsn of temporary db
    :return:
    """
    engine = create_engine(db_with_test_data)
    # engine = create_engine(db_with_test_data, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    test_urls = { r.url for r in session.query(
        perfsonar_data.model.Doc).all() }

    assert test_urls == set(_TEST_DATA_FILES.keys())


def test_esmond_group_by_participants(
        db_with_test_data, esmond_base_url):
    """
    sanity test on group_by_participants

    test data contains non-zero number of participants
    :param db_with_test_data:
    :return:
    """
    proxy.init_db_engine(dsn=db_with_test_data)

    tests = esmond.load_tests(esmond_base_url)
    num_participants = 0
    for g in esmond.group_by_participants(tests):
        logging.info("participants: " + str(g["participants"]))
        logging.info("  num tests: %d" % len(g["tests"]))
        num_participants += 1

    assert num_participants > 0, "test data contained participiants, but none found"


def test_esmond_group_by_tool(db_with_test_data, esmond_base_url):
    """
    sanity test on group_by_tool

    test data contains non-zero number of tools
    :param db_with_test_data:
    :return:
    """
    proxy.init_db_engine(dsn=db_with_test_data)

    tests = esmond.load_tests(esmond_base_url)
    num_tools = 0
    for name, tests in esmond.group_by_tool(tests).items():
        logging.info("'%s': %d tests" % (name, len(tests)))
        num_tools += 1

    assert num_tools > 0, "test data contained tools, but none found"
