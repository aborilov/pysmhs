from setuptools import setup, find_packages
import sys

setup(
    name="pysmhs",
    version="1.0.4",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ('etc/pysmhs',
         ['config/coreconfig.txt', 'config/actions.txt',
          'config/dateconfig.txt', 'config/tags_config.txt'])],
    include_package_data=True,
    author="Aborilov Pavel",
    description="Smart House Control System",
    author_email = 'aborilov@gmail.com',
    url = 'http://www.pysmhs.org/',
    download_url = 'https://github.com/aborilov/pysmhs/archive/develop.zip',
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
