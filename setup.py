from setuptools import setup, find_packages

setup(
    name="esmond_helper",
    version="0.1",
    description="esmond helper/proxy",
    packages=find_packages(exclude=("tests",)),
    install_requires=[
        "requests",
        "alembic",
        "flask",
        "flask-sqlalchemy",
        "flask-migrate",
        "jsonschema",
        "gunicorn",
    ]
)
