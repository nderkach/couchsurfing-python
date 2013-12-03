class Messages(object):
    """ Private messages
    """
    def __init__(self, api, mtype="inbox", limit=10):
        self._api = api
        assert(mtype in ("inbox", "sent"))
        url = "https://api.couchsurfing.org/users/{0.uid}/messages".format(
            self._api)
        response = self._api.get(url, params= {"type": mtype, "limit": limit})
        self.messages = response.json()['object']
        self.version = response.json()['version']
        self.after = response.json()['after']

    def get_unread(self, with_couch_request=False):
        """ Get unread messages
        """
        for message in self.messages:
            print(message)
            # TODO: send requests in parallel
            response = self._api.get(message)
            # user = response.json()["user"]["url"]
            # title = response.json()["title"]
            # date = response.json()["date"]
            message = response.json()["message"]
            if (not response.json()["user_is_sender"] and
                response.json()["is_unread"] and
                (with_couch_request or (not with_couch_request and
                                    "couchrequest" not in response.json()))):
                print(message)
