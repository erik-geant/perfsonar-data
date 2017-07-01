import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import perfsonar_data
import data

@pytest.fixture
def empty_db():
    """
    yields a dsn to a temporary database

    the temporary database file is deleted once context mgmt is complete

    :return: dsn (string)
    """
    import tempfile
    from alembic.config import Config
    from alembic import command

    fd, name = tempfile.mkstemp()
    os.close(fd)

    dsn = "sqlite:///" + name  # careful: assumes linux separators

    cfg = Config(os.path.join(perfsonar_data.__path__[0], "alembic.ini"))
    cfg.set_main_option("script_location",
                        os.path.join(perfsonar_data.__path__[0], "migrations"))
    cfg.set_main_option("sqlalchemy.url", dsn)
    command.upgrade(cfg, revision="head")

    try:
        yield dsn
    finally:
        # don't fill the disk with tmp db files
        os.unlink(name)


@pytest.fixture
def db_with_test_data(empty_db):
    """
    returns a dsn to a temporary database

    :param empty_db:
    :return: dsn (string)
    """

    engine = create_engine(empty_db)
    # engine = create_engine(empty_db, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    for url, filename in data.TEST_DATA_FILES.items():

        if session.query(perfsonar_data.model.Doc) \
                .filter(perfsonar_data.model.Doc.url == url) \
                .first() is not None:
            continue


        with open(os.path.join(data.DATA_PATH, filename),
                  encoding="utf-8") as f:
            session.add(perfsonar_data.model.Doc(
                url=str(url), doc=f.read()))

        session.commit()

    session.close()
    engine.dispose()

    return empty_db


