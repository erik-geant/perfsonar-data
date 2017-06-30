import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "data")

ESMOND_BASE_URL = "http://158.125.250.70/"
TEST_DATA_FILES = {
    # ACTIVE_HOSTS
    "http://ps-west.es.net:8096/lookup/activehosts.json": "activehosts.json",

    # HOST_RECORDS
    "http://ps-west.es.net:8090/lookup/records": "records.ps-west",
    "http://ps-east.es.net:8090/lookup/records": "records.ps-east",
    "http://monipe-ls.rnp.br:8090/lookup/records": "records.monipe-ls",
    "http://ps-sls.sanren.ac.za:8090/lookup/records": "records.ps-sls.sanren",
    "http://nsw-brwy-sls1.aarnet.net.au:8090/lookup/records/": "records.aarnet",

    # TEST_ARCHIVE
    ESMOND_BASE_URL + "esmond/perfsonar/archive/": "archive.json",
}

