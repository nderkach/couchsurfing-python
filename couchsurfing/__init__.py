#!/usr/bin/env python

"""
Python wrapper for api.couchsurfing.org
"""

from datetime import datetime
import getpass
import requests

CS_URL = "https://api.couchsurfing.org"

from couchsurfing.couchrequests import CouchRequests
from couchsurfing.messages import Messages
from couchsurfing.api import Api
