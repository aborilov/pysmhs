from setuptools import setup, find_packages
import sys

setup(
    name="pysmhs",
    version="1.0.1",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ('etc/pysmhs',
         ['config/coreconfig.txt', 'config/actions.txt',
          'config/dateconfig.txt', 'config/tags_config.txt'])],
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
    scripts=["bin/pysmhs"]
    )
