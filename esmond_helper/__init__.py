"""
factory for use with flask blueprints
"""
import os
from flask import Flask


def create_app():
    app = Flask("esmond-helper")
    app.config.from_object("esmond_helper.default_settings")
    if "SETTINGS_FILENAME" in os.environ:
        app.config.from_envvar("SETTINGS_FILENAME")

    from esmond_helper.server import server as old_server
    app.register_blueprint(old_server)

    from esmond_helper.grafana import server as grafana_server
    app.register_blueprint(grafana_server, url_prefix="/grafana")

    return app
