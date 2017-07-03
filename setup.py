from setuptools import setup, find_packages

setup(
    name="perfsonar_data",
    version="0.1",
    description="perfsonar data consolidation tools",
    packages=find_packages(exclude=("tests",)),
    install_requires=[
        "requests",
        "alembic",
        "flask",
        "flask-sqlalchemy",
        "flask-migrate",
        "jsonschema",
    ]
)
