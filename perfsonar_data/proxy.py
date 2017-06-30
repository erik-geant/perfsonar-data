import json
import logging

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import model


_engine = None
_session_maker = None

def init_db_engine(dsn="sqlite://"):
    global _engine
    global _session_maker
    _engine = create_engine(dsn)
    # _engine = create_engine(dsn, echo=True)
    _session_maker = sessionmaker(bind=_engine)


def load_url_json(url):

    assert _engine is not None and _session_maker is not None, \
        "db engine not initialized, call init_db_engine before using the proxy"

    session = _session_maker()

    row = session.query(model.Doc).filter(model.Doc.url==url).first()
    if row is not None:
        logging.debug("proxy hit for '%s'" % url)
        return json.loads(row.doc)

    logging.debug("downloading from '%s'" % url)

    r = requests.get(url)
    assert r.status_code == 200
    assert "application/json" in r.headers["content-type"]
    data = r.json()

    session.add(model.Doc(url=url, doc=json.dumps(data)))
    session.commit()
    session.close()

    logging.debug("saved new document for '%s'" % url)
    return data

