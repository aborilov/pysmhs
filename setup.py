from setuptools import setup, find_packages

setup(
    name="pysmhs",
    version="1.0",
    packages=find_packages(exclude=["test"]),
    include_package_data=True,
    author="Aborilov Pavel",
    description="PySMHS",
    install_requires=[
        "Jinja2",
        "Twisted",
        "pymodbus",
        "pyserial",
        "python-dateutil",
        "louie"
    ],
    )
