import json
import logging
import time

from flask import current_app
import redis
import requests

# from esmond_helper import model

_24H_SECONDS = 24 * 60 * 60
_DEFAULT_EXPIRATION = _24H_SECONDS


def db(config=None):
    if config is None:
        config = current_app.config["REDIS_PARAMS"]
    return redis.StrictRedis(
        host=config["hostname"],
        port=config["port"])


def load_url_json(url, connection, expires=_DEFAULT_EXPIRATION+int(time.time())):

    # session.query(model.Doc) \
    #     .filter(model.Doc.expires < int(time.time())) \
    #     .delete()
    # session.commit()
    #
    # row = session.query(model.Doc).filter(model.Doc.url == url).first()
    # if row is not None:
    #         logging.debug("proxy hit for '%s'" % url)
    #         return json.loads(row.doc)

    data = connection.get(url)
    if data is not None:
        logging.debug("proxy hit for '%s'" % url)
        return json.loads(data.decode('utf-8'))

    logging.debug("downloading from '%s'" % url)

    r = requests.get(url)
    assert r.status_code == 200
    assert "application/json" in r.headers["content-type"]
    data = r.json()

    connection.set(url, r.content, ex=expires)

    # session.add(model.Doc(url=url, expires=expires, doc=json.dumps(data)))
    # session.commit()

    logging.debug("saved new document for '%s'" % url)
    return data
