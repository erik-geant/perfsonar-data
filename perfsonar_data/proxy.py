import json
import logging
import time

import requests

from perfsonar_data import model

_24H_SECONDS = 24 * 60 * 60
_DEFAULT_EXPIRATION = _24H_SECONDS


def load_url_json(url, session, expires=_DEFAULT_EXPIRATION+int(time.time())):

    session.query(model.Doc) \
        .filter(model.Doc.expires < int(time.time())) \
        .delete()
    session.commit()

    row = session.query(model.Doc).filter(model.Doc.url == url).first()
    if row is not None:
            logging.debug("proxy hit for '%s'" % url)
            return json.loads(row.doc)

    logging.debug("downloading from '%s'" % url)

    r = requests.get(url)
    assert r.status_code == 200
    assert "application/json" in r.headers["content-type"]
    data = r.json()

    session.add(model.Doc(url=url, expires=expires, doc=json.dumps(data)))
    session.commit()

    logging.debug("saved new document for '%s'" % url)
    return data
