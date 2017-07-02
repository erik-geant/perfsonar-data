"""
entry point that can be invoked as:

    FLASK_APP=perfsonar_data.app flask run

or just by running the module directly
"""
from perfsonar_data import app_factory

# TODO: take dsn & port from somewhere ...?

app = app_factory.create_app()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8234)

