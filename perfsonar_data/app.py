import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask("perfsonar_data")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/perfsonar-data.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# this is actually the default, but maybe worth being explicit
ALEMBIC_MIGRATION_DIRECTORY = os.path.join(
    os.path.dirname(__file__),
    "migrations")

db = SQLAlchemy(app)
migrate = Migrate(app, db, directory=ALEMBIC_MIGRATION_DIRECTORY)
