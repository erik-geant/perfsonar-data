import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import perfsonar_data
import data

logging.basicConfig(level=logging.INFO)


def test_testdata(db_with_test_data):
    """
    basic sanity test on the test db creation
    :param db_with_test_data: dsn of temporary db
    """
    engine = create_engine(db_with_test_data)
    # engine = create_engine(db_with_test_data, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    test_urls = { r.url for r in session.query(
        perfsonar_data.model.Doc).all() }

    assert test_urls == set(data.TEST_DATA_FILES.keys())

