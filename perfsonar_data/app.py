import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask("perfsonar_data")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/perfsonar-data.sqlite"
# this is actually the default, but maybe worth being explicit
ALEMBIC_MIGRATION_DIRECTORY = os.path.join(
    os.path.dirname(__file__),
    "migrations")

db = SQLAlchemy(app)
migrate = Migrate(app, db, directory=ALEMBIC_MIGRATION_DIRECTORY)
