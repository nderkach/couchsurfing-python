#!/usr/bin/env python

import os
from distutils.core import setup

PROJECT = 'Couchsurfing API'
VERSION = '0.1'
URL = 'https://github.com/nderkach/couchsurfing-python'
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
    # long_description=read_file('README.rst'),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=read_file('LICENSE'),
    packages=['couchsurfing'],
    classifiers=[
    	# see http://pypi.python.org/pypi?:action=list_classifiers
        # -*- Classifiers -*- 
        "Programming Language :: Python",
    ],
)
