from setuptools import setup, find_packages

setup(
    name="esmond_helper",
    version="0.3",
    description="esmond helper/proxy",
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
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
