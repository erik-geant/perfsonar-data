import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

_DEFAULT_DSN = "sqlite:////tmp/perfsonar-data.sqlite"

app = Flask("perfsonar_data")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "SQLALCHEMY_DATABASE_URI", _DEFAULT_DSN)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# this is actually the default, but maybe worth being explicit
ALEMBIC_MIGRATION_DIRECTORY = os.path.join(
    os.path.dirname(__file__),
    "migrations")

db = SQLAlchemy(app)
migrate = Migrate(app, db, directory=ALEMBIC_MIGRATION_DIRECTORY)
