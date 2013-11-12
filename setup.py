#!/usr/bin/env python

# Bootstrap installation of Distribute
import distribute_setup
distribute_setup.use_setuptools()

import os

from setuptools import setup


PROJECT = 'Couchsurfing API'
VERSION = '0.1'
URL = ''
AUTHOR = 'Nikolay Derkach'
AUTHOR_EMAIL = 'nderk@me.com'
DESC = "A short description..."

def read_file(file_name):
    file_path = os.path.join(
        os.path.dirname(__file__),
        file_name
        )
    return open(file_path).read()

setup(
    name=PROJECT,
    version=VERSION,
    description=DESC,
    long_description=read_file('README.rst'),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=read_file('LICENSE'),
    namespace_packages=[],
    packages=['couchsurfing'],
    package_dir = {'': os.path.dirname(__file__)},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Requirements -*-
	requests
    ],
    entry_points = {
        # -*- Entry points -*-
    },
    classifiers=[
    	# see http://pypi.python.org/pypi?:action=list_classifiers
        # -*- Classifiers -*- 
        "Programming Language :: Python",
    ],
)
