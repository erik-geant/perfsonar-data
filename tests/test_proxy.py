import logging

# from esmond_helper import model

from . import data

logging.basicConfig(level=logging.INFO)


def test_testdata(mocked_test_redis):
    """
    basic sanity test on the test db creation
    :param db_with_test_data: flask app and sqlalchemy session instances
    """

    # test_urls = {r.url for r in
    #              db_with_test_data["session"].query(model.Doc).all()}
    #
    # assert test_urls == set(data.TEST_DATA_FILES.keys())
    pass