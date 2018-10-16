"""
testing entry point that can be invoked as:

    FLASK_APP=perfsonar_data.app flask run

or just by running the module directly
"""

if __name__ == "__main__":
    import logging
    import sys
    import perfsonar_data

    logging.basicConfig(
        stream=sys.stderr,
        level=logging.DEBUG)

    app = perfsonar_data.create_app()
    app.run(host="0.0.0.0", port="8234")

