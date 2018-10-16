import logging

from esmond_helper import sls
from tests import data

logging.basicConfig(level=logging.INFO)


def test_sls_bootstrap(db_with_test_data):
    """
    location bootstrap sanity check

    test data should contain more than one host
    :param db_with_test_data: flask app and sqlalchemy session instances
    """

    hosts = list(sls.download_lookup_data(
        data.SLS_BOOTSTRAP_URL,
        db_with_test_data["session"]))
    assert len(hosts) > 0, "test data should have contained at least 1 host"
    assert len(hosts) == 1792, \
        "bogus test just to snapshot the current test data & code state"
