#!/usr/bin/env python

import time
from calendar import timegm
from datetime import datetime
import re
import getpass

import requests

CS_URL = "https://api.couchsurfing.org"

class AuthException(Exception):
	pass

class Api(object):
	""" Base API class"""
	def __init__(self, username=None, password=None, uid = None, cookies = None):
		self._session = requests.Session()
		if cookies:
			# check if we already have a cookie to authenticate our session with
			assert(uid and isinstance(cookies, requests.cookies.RequestsCookieJar))
			self._session.cookies = cookies
			self._uid = uid
			# TODO: there could be a way to get uid from the API
			# otherwise we'll have to store the mapping uid -> session cookie elsewhere
		else:
			# otherwise run a post to get one
			assert(username and password)
			r = self._session.post('https://api.couchsurfing.org/sessions',
		                      data={"username": username, "password": password})
			if (r.status_code != 200):
				raise AuthException
			self._uid = r.json()["url"].split('/')[-1]
		self.get = self._session.get

	@property
	def uid(self):
		return self._uid

	@property
	def cookies(self):
		return self._session.cookies

class Messages():
	""" Private messages """
	def __init__(self, api, mtype="inbox", limit=10):
		self._api = api
		assert(mtype in ("inbox", "sent"))
		url = "https://api.couchsurfing.org/users/{0.uid}/messages".format(self._api)
		r = self._api.get(url, params= {"type": mtype, "limit": limit})
		self.messages = r.json()['object']
		self.version = r.json()['version']
		self.after = r.json()['after']

	def get_unread(self, with_couch_request=False):
		for message in self.messages:
			# TODO: send requests in parallel
			r = self._api.get(message)
			user = r.json()["user"]["url"]
			title = r.json()["title"]
			date = r.json()["date"]
			message = r.json()["message"]
			if (not r.json()["user_is_sender"] and r.json()["is_unread"] and
			    (with_couch_request or (not with_couch_request and
			    					    "couchrequest" not in r.json()))):
				print(message)

class Requests(object):
	""" Couch requests within (start, end)
	"""
	def __init__(self, api, start=60*24*3600, end=None):
		t = time.time()
		self._api = api
		url = "https://api.couchsurfing.org/users/{0.uid}/couchrequests".format(
			self._api)

		"""
			"since" refers to request creation date
			we check for all the requests created in the last 2 months

		"""
		payload = {"since": start-60*24*3600, "expand": "couchrequests,users"}

		r = self._api.get(url, params=payload)

		self._new = []
		self._accepted = []
		_id = 0

		if 'object' not in r.json():
			raise Exception("No object in response")

		self._requests = r.json()['object']

		def get_timestamp(timestr):
			return timegm(time.strptime(timestr.replace('Z', 'GMT'),
											  "%Y-%m-%dT%H:%M:%S%Z"))

		for request in self._requests:
			arrival = get_timestamp(request['arrival'])
			departure = get_timestamp(request['departure'])

			if departure < start or (end and arrival > end):
				continue

			if request['status'] != "declined":
				url = "https://couchsurfing.org/couchmanager?read={0}".format(
					request['url'].split('/')[-1])
				name = "{0} from {1}".format(request["surfer_user"]["realname"],
			    	request["surfer_user"]["address"]["country"])

				if request['status'] in ("maybe", "new"):
					self._new.append({"id": _id, "title": name,
									  "url": url, "class": "event-warning",
									  "start": arrival,
									  "end": departure })
					_id +=1

				elif request['status'] == "accepted":
					self._accepted.append({"id": _id, "title": name,
										   "url": url, "class": "event-success",
										   "start": arrival,
										   "end": departure })
					_id +=1

	@property
	def accepted(self):
		return self._accepted

	@property
	def new(self):
		return self._new


if __name__ == "__main__":
	login = input("Login: ")
	password = getpass.getpass()

	# test API with login and password
	api = Api(login, password)
	print(api.uid)

	# login with a session cookie received on a previous authentication
	api2 = Api(uid=api.uid, cookies=api.cookies)
	print(api2.uid)

	messages = Messages(api, "inbox")
	messages.get_unread()

	now = datetime.now()
	start_month = int(datetime(now.year, now.month, 1).timestamp())
	end_month = int(datetime(now.year, now.month%12+1, 1).timestamp())

	requests = Requests(api, start_month, end_month)
	print(requests.accepted)
	print(requests.new)
	print("Total: ", len(requests.accepted+requests.new))