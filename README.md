couchsurfing-python
===================

*UPDATE*: this package is not actively mainated anymore

I also wrote a guide (https://www.toptal.com/back-end/reverse-engineering-the-private-api-hacking-your-couch) about the techniques I used to reverse engineer this and other APIs.

Couchsurfing.org Python API

.. image:: https://badge.fury.io/py/couchsurfing.svg
    :target: http://badge.fury.io/py/couchsurfing

Requirements
------------

* requests

Usage:
------

* Initialize API with couchsurfing.org username and password::

	from couchsurfing import Api
	api = Api(login, password)

* Get your user profile::

	api.get_profile()

* Get the profile of someone else::

        api.get_profile_by_id(userID)

* Get the friends of someone else::

        api.get_friendlist(userID)

* Get the references of someone else::

        api.get_references(userID, type)

* Get events in some place::

        api.get_events("48.1078396751677,11.5792098447259")
        # you can get lat/lng from google geocoding api
	
* Get hosts in some place::

        api.get_hosts((place_name="Madrid, Spain",
                       filters={'sleepingArrangements':'privateRoom'})

* Get visitors in some place::

        api.get_visits((place_name="Madrid, Spain",
                       filters={'isVerified': 1})

.. image:: https://travis-ci.org/nderkach/couchsurfing-python.png
    :target: https://travis-ci.org/nderkach/couchsurfing-python
