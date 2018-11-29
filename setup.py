from setuptools import setup, find_packages

setup(
    name="esmond-helper",
    version="0.12",
    description="esmond helper/proxy",
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=[
        "requests",
        "flask",
        "jsonschema",
        "redis",
    ]
)
