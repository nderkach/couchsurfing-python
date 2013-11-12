#!/usr/bin/env python

import requests
import datetime
import re
import timeit

from requests_futures.sessions import FuturesSession


AUTH = {"username": "nderkach", "password": "Nnd121088!"}
CS_URL = "https://api.couchsurfing.org"

class AuthException(Exception):
	pass

class Api(object):
	""" Base API class"""
	def __init__(self, username=AUTH["username"], password=AUTH["password"]):
		# self._session = requests.Session()
		self._session = FuturesSession(max_workers=10)
		r = self._session.post('https://api.couchsurfing.org/sessions',
		                      data={"username": username, "password": password}).result()
		# print({"username": "{0}".format(username), "password": "{0}".format(password)})
		if (r.status_code != 200):
			raise AuthException
		self._uid = r.json()["url"].split('/')[-1]
		# print(self._uid)
		# print(r.headers)

	def __repr__(self):
		print("couchsurfing.Api()")

	def __str__(self):
		print("CouchSurfing API: Logged in as {0.realname} ({0.username})".format(self.data))

class Messages(Api):
	""" Private messages """
	def __init__(self, mtype="inbox", limit=10):
		super().__init__()
		assert(mtype in ("inbox", "sent"))
		url = "https://api.couchsurfing.org/users/{0._uid}/messages".format(self)
		r = self._session.get(url, params= {"type": mtype, "limit": limit}).result()
		self.messages = r.json()['object']
		self.version = r.json()['version']
		self.after = r.json()['after']
		# for message in self.messages:
		# 	r = self._session.get(message)
		# 	print(r.json())

	def get_unread(self, with_couch_request=False):
		for message in self.messages:
			# TODO: send requests in parallel
			r = self._session.get(message).result()
			user = r.json()["user"]["url"]
			title = r.json()["title"]
			date = r.json()["date"]
			message = r.json()["message"]
			if (not r.json()["user_is_sender"] and r.json()["is_unread"] and
			    (with_couch_request or (not with_couch_request and "couchrequest" not in r.json()))):
				print(r.json())
				print(message)

class Requests(Api):
	""" Couch requests """
	def __init__(self, start = 0, end = float("inf")):
		super().__init__()
		url = "https://api.couchsurfing.org/users/{0._uid}/couchrequests".format(self)
		r = self._session.get(url).result()
		
		# print(r.json())

		# print("GOT LIST OF REQUESTS", len(r.json()['object']))

		self._requests = r.json()['object']
		# print(self.requests)
		# self._version = r.json()['version']
		# self._after = r.json()['after']
		# print(self._version)
		# print(self._after)
		self._new = []
		self._accepted = []
		id = 0

		def get_timestamp(timestr):
			return datetime.datetime.strptime(timestr, "%Y-%m-%dT%H:%M:%SZ").timestamp()

		request_list = set()

		for request in self._requests:
			# print("request")
			request_list.add(self._session.get(request))

		for request in request_list:
			# print("processing")
			r = request.result()
			json = r.json()
			# print(json)

			arrival = get_timestamp(json['arrival'])
			# print(arrival)
			departure = get_timestamp(json['departure'])

			# if not start < arrival < departure < end:
			# 	# print (arrival, departure)
			# 	continue

			if json['status'] == "new" and not json['is_expired']:
				# print(json)
				url = "https://couchsurfing.org/couchmanager?read={0}".format(json['url'].split('/')[-1])
				find = re.findall(r'(.*) sent', str(json['subject']))
				name = find if find else json['subject']
				self._new.append({"id": str(id), "title": name, "url": url,
								  "class": "event-warning", "start": str(int(arrival)*1000), "end": str(int(departure)*1000) })
				id +=1
				# print("append new")

			elif json['status'] == "accepted":
				# print(json)
				url = "https://couchsurfing.org/couchmanager?read={0}".format(json['url'].split('/')[-1])
				find = re.findall(r'(.*) sent', str(json['subject']))
				name = find if find else json['subject']
				self._accepted.append({"id": str(id), "title": name, "url": url,
								  "class": "event-info", "start": str(int(arrival)*1000), "end": str(int(departure)*1000) })
				id +=1
				# print("append accepted")

		# for n in self._new:
		# 	for a in self._accepted:
		# 		if (a[0] <= n[0] <= a[1]) or (n[0] <= a[0] <= n[1]):
		# 			print(n, a)

	@property
	def accepted(self):
		# accepted = set()
		# for daterange in self._accepted:
		# 	for datetm in (daterange[0] + datetime.timedelta(n) for n in range((daterange[1]-daterange[0]).days + 1)):
		# 		accepted.add(datetm.date())
		return self._accepted

	@property
	def new(self):
		# new = set()
		# for daterange in self._new:
		# 	for datetm in (daterange[0] + datetime.timedelta(n) for n in range((daterange[1]-daterange[0]).days + 1)):
		# 		new.add(datetm.date())
		return self._new

	# @accepted.setter
	# def accepted(self, value):
	# 	self.accepted = value

	# @new.setter
	# def new(self, value):
	# 	self.new = value






if __name__ == "__main__":
	ap = Api()
	messages = Messages("inbox")

	now = datetime.datetime.now()
	start_month = datetime.datetime(now.year, now.month, 1)

	requests = Requests(start_month.timestamp(), now.timestamp())
	# print(requests.accepted)
	# print(requests.new)
	# print("Total: ", len(requests.accepted+requests.new))