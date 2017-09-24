import requests
import hmac
from hashlib import sha1
import json
try:
    from urllib.parse import urlencode
except ImportError:
    # python2
    from urllib import urlencode

CS_URL = "https://hapi.couchsurfing.com"
PRIVATE_KEY = "v3#!R3v44y3ZsJykkb$E@CG#XreXeGCh"


class AuthError(Exception):
    """
    Authentication error
    """
    def __init__(self, arg):
        print('AuthError: ' + str(arg))


class RequestError(Exception):
    """
    Request error
    """
    pass


class Api(object):
    """ Base API class
    >>> api = Api("nzoakhvi@sharklasers.com", "qwerty")
    >>> api.uid
    1003669205
    >>> api.get_profile() # doctest: +ELLIPSIS
    {...}
    >>> api.get_profile_by_id('1003669205') # doctest: +ELLIPSIS
    {...}
    >>> api.get_friendlist('1003669205') # doctest: +ELLIPSIS
    {...}
    >>> api.get_references('1003669205', 'surf') # doctest: +ELLIPSIS
    {...}
    >>> api = Api("foo", "bar") # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    AuthError
    """

    def get_url_signature(self, key, msg):
        return hmac.new(
            key.encode("utf-8"), msg.encode("utf-8"), sha1).hexdigest()

    def __init__(self, username=None, password=None,
                 uid=None, access_token=None):
        self._session = requests.Session()
        if uid and access_token:
            self.uid = uid
            self._access_token = access_token

        else:
            assert(username and password)
            login_payload = {"actionType":
                             "manual_login",
                             "credentials":
                             {"authToken": password, "email": username}}

            signature = self.get_url_signature(
                PRIVATE_KEY,
                "/api/v3/sessions" + json.dumps(login_payload)
            )

            self._session.headers = {
                "Accept": "application/json",
                "X-CS-Url-Signature": signature,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "en;q=1",
                "Content-Type": "application/json; charset=utf-8",
                "User-Agent": """Dalvik/2.1.0 (Linux; U; Android 5.0.1;"""
                """ Android SDK built for x86 Build/LSX66B) Couchsurfing"""
                """/android/20141121013910661/Couchsurfing/3.0.1/ee6a1da"""
            }

            r = self._session.post(
                CS_URL+"/api/v3/sessions", data=json.dumps(login_payload)
            )

            if "sessionUser" not in r.json():
                raise AuthError(r.json())
            r.raise_for_status()
            self.uid = int(r.json()["sessionUser"]["id"])
            self._access_token = r.json()["sessionUser"]["accessToken"]

    def api_request(self, path):
        """
        Request api for certain path
        """
        assert(self._access_token)

        signature = self.get_url_signature(
            "{0}.{1}".format(PRIVATE_KEY, self.uid), path
        )
        self._session.headers.update({
            "X-CS-Url-Signature": signature,
            "X-Access-Token": self._access_token
        })
        r = self._session.get(CS_URL + path)

        if (r.status_code != 200):
            raise RequestError

        return r.json()

    def get_friendlist(self, uid, perPage=999999999):
        """
        Ask for friendlist for specific user
        """
        path = (
            "/api/v3.1/users/" + str(uid) +
            "/friendList/friends?perPage=" + str(perPage) +
            "&page=1&includeMeta=false"
        )

        return self.api_request(path)

    def get_profile(self):
        """
        Ask for your own profile
        """
        path = "/api/v3/users/" + str(self.uid)

        return self.api_request(path)

    def get_profile_by_id(self, uid):
        """
        Ask for specific user's profile
        """
        path = "/api/v3/users/" + str(uid)

        return self.api_request(path)

    def get_events(self, latlng, perpage=100):
        """
        Search for events
        """
        path = ("/api/v3.2/events/search"
                "?page=1&perPage={perpage}&latLng={latlng}".format(
                    perpage=perpage, latlng=latlng))

        return self.api_request(path)

    def get_visits(self, place_name, radius=10,
                   perpage=100, place_id=None, filters=None):
        """
        Search for visitors by place_name. Place_id is not mandatory.
        Optionally pass filters as a dict with possible values:
            maxAge=100, minAge=18, countries="DEU,UKR", hasReferences=1,
            gender=male, fluentLanguages="ukr,deu", isVerified=1,
            keyword="some-keyword"
        """
        params = {
            'page': 1,
            'perPage': perpage,
            'placeDescription': place_name,
            'placeId': place_id,
            'radius': radius,
        }
        if filters:
            params.update(filters)
        query = urlencode(params)
        path = "/api/v3.2/visits/search?%s" % query

        return self.api_request(path)

    def get_hosts(self, place_name, radius=10,
                  perpage=100, place_id=None, sort='best_match',
                  couch_status="yes,maybe",
                  filters=None):
        """
        Search for hosts in place_name. Place_id is not mandatory.
        Optionally pass filters as a dict with possible values:
            sleepingArrangements='privateRoom', minGuestsWelcome=2
            maxAge=100, minAge=18, hasReferences=1,
            gender=female, fluentLanguages="ukr,deu", isVerified=1,
            keyword="some-keyword"
        """
        params = {
            'page': 1,
            'perPage': perpage,
            'placeDescription': place_name,
            'placeId': place_id,
            'radius': radius,
            'sort': sort,
            'couchStatus': couch_status,
        }
        if filters:
            params.update(filters)
        query = urlencode(params)
        path = "/api/v3.2/users/search?%s" % query

        return self.api_request(path)

    def get_references(self, uid, type, perPage=999999999):
        """
        Ask for references

        type -- surf, host, other_and_friend
        """
        path = (
            "/api/v3/users/" + str(uid) +
            "/references?perPage=" + str(perPage) +
            "&relationshipType=" + type + "&includeReferenceMeta=true"
        )

        return self.api_request(path)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
