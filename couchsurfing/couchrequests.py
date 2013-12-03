from calendar import timegm
import re
import time

class CouchRequests(object):
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
                    _id += 1

                elif request['status'] == "accepted":
                    self._accepted.append({"id": _id, "title": name,
                                           "url": url, "class": "event-success",
                                           "start": arrival,
                                           "end": departure })
                    _id += 1

    @property
    def accepted(self):
        return self._accepted

    @property
    def new(self):
        return self._new
