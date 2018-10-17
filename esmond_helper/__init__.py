"""
factory for use with flask blueprints
"""
import os
from flask import Flask
from flask_migrate import Migrate

from esmond_helper.model import db


def create_app():
    app = Flask("esmond-helper")
    app.config.from_object("esmond_helper.default_settings")
    if "SETTINGS_FILENAME" in os.environ:
        app.config.from_envvar("SETTINGS_FILENAME")

    # this is actually the default, but maybe worth being explicit
    ALEMBIC_MIGRATION_DIRECTORY = os.path.join(
        os.path.dirname(__file__),
        "migrations")

    db.init_app(app)

    Migrate(app, db, directory=ALEMBIC_MIGRATION_DIRECTORY)
    # migrate = Migrate(app, db, directory=ALEMBIC_MIGRATION_DIRECTORY)

    # cf. http://flask.pocoo.org/docs/0.10/patterns/appfactories/
    from esmond_helper.server import server
    app.register_blueprint(server)

    return app
