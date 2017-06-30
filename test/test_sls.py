import logging

from perfsonar_data import sls
from perfsonar_data import proxy
import data

logging.basicConfig(level=logging.INFO)


def test_sls_bootstrap(db_with_test_data):
    """
    location bootstrap sanity check

    test data should contain more than one host
    :param db_with_test_data: dsn of temporary db
    """
    proxy.init_db_engine(db_with_test_data)

    hosts = list(sls.download_lookup_data(data.SLS_BOOTSTRAP_URL))
    assert len(hosts) > 0, "test data should have contained at least 1 host"
    assert len(hosts) == 1792, "bogus test just to snapshot the current test data & code state"
