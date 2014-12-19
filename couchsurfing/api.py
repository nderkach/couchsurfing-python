import requests
import hmac
from hashlib import sha1
import json

CS_URL = "https://hapi.couchsurfing.com"
PRIVATE_KEY = "v3#!R3v44y3ZsJykkb$E@CG#XreXeGCh"


class AuthError(Exception):
    """
    Authentication error
    """
    pass


class RequestError(Exception):
    """
    Incorrect response when querying API
    """
    pass


class Api(object):
    """ Base API class
    >>> api = Api("nzoakhvi@sharklasers.com", "qwerty")
    >>> api.uid
    1003669205
    >>> api.get_profile() # doctest: +ELLIPSIS
    {...}
    >>> api = Api("foo", "bar") # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    AuthError
    """

    def get_url_signature(self, key, msg):
        return hmac.new(key.encode("utf-8"), msg.encode("utf-8"),
                        sha1).hexdigest()

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
                "/api/v2/sessions"+json.dumps(login_payload)
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
                CS_URL+"/api/v2/sessions", data=json.dumps(login_payload)
            )

            if (r.status_code != 200 or "sessionUser" not in r.json()):
                raise AuthError
            self.uid = int(r.json()["sessionUser"]["id"])
            self._access_token = r.json()["sessionUser"]["accessToken"]

    def get_profile(self):
        assert(self._access_token)

        path = "/api/v2/users/" + str(self.uid)

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


if __name__ == "__main__":
    import doctest
    doctest.testmod()
