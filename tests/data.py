import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "data")

ESMOND_BASE_URL = "http://158.125.250.70/"
SLS_BOOTSTRAP_URL = "http://ps-west.es.net:8096/lookup/activehosts.json"

_ESMOND_ARCHIVE_PATH = "esmond/perfsonar/archive/"

OWDELAY_HISTOGRAM_ID = \
    "297d7757f0524a06a7c45463f3bba0a6/histogram-owdelay/statistics/300"
THROUGHPUT_ID = \
    "095c3f53ada84b7a91d4f1dbd9c5b7ca/throughput/averages/86400"

TEST_DATA_FILES = {
    # ACTIVE_HOSTS
    SLS_BOOTSTRAP_URL: "activehosts.json",

    # HOST_RECORDS
    "http://ps-west.es.net:8090/lookup/records":
        "records.ps-west",
    "http://ps-east.es.net:8090/lookup/records":
        "records.ps-east",
    "http://monipe-ls.rnp.br:8090/lookup/records":
        "records.monipe-ls",
    "http://ps-sls.sanren.ac.za:8090/lookup/records":
        "records.ps-sls.sanren",
    "http://nsw-brwy-sls1.aarnet.net.au:8090/lookup/records/":
        "records.aarnet",
    "http://perfsonar.debrecen3.hbone.hu/esmond/perfsonar/archive/":
        "debrecen3-archive.json",
    "http://perfsonar.debrecen3.hbone.hu/esmond/perfsonar/archive/055e327da6484ce5959dd51a93c93ed5/packet-count-sent/aggregations/86400":  # noqa: ignore=E501
        "debrecen3-86400.json",
    "http://64.106.40.252//esmond/perfsonar/archive/38db04b7baf04ff5aa26af689b33fd4d/packet-count-lost/aggregations/86400":  # noqa: ignore=E501
        "esmond-packet-count-lost-86400.json",
    "http://64.106.40.252//esmond/perfsonar/archive/":
        "esmond-archive.json",

    # TEST_ARCHIVE
    ESMOND_BASE_URL + _ESMOND_ARCHIVE_PATH: "archive.json",

    # SUMMARIES
    ESMOND_BASE_URL + _ESMOND_ARCHIVE_PATH + OWDELAY_HISTOGRAM_ID: \
        "histogram-owdelay-300.json",
    ESMOND_BASE_URL + _ESMOND_ARCHIVE_PATH + THROUGHPUT_ID: \
        "throughput-86400.json",
}
