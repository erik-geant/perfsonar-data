import requests

PS_BASE_URL = "http://192.87.30.58/"
def _esmond_url(base=PS_BASE_URL):
    return base + "esmond/perfsonar/archive/"



r = requests.get(_esmond_url())
assert r.status_code
assert "application/json" in r.headers["content-type"]

archive = r.json()
assert isinstance(archive, [list, tuple])

