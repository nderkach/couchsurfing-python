couchsurfing-python
===================

Couchsurfing.org Python API

.. image:: https://badge.fury.io/py/couchsurfing.svg
    :target: http://badge.fury.io/py/couchsurfing

Usage:
------

* Initialize API with couchsurfing.org username and password::

	from couchsurfing import Api
	api = Api(login, password)

* Get you user profile::

	api.get_profile()
	
.. image:: https://travis-ci.org/nderkach/couchsurfing-python.png
    :target: https://travis-ci.org/nderkach/couchsurfing-python
