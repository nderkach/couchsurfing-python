import requests

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
    """
    # >>> api = Api("foo", "bar") # doctest: +IGNORE_EXCEPTION_DETAIL
    # Traceback (most recent call last):
    # ...
    # couchsurfing.api.AuthError
    #
    # WAT: the exception doctest doesn't work with py2.7:
    # http://bugs.python.org/issue19138

    def __init__(self, username=None, password=None,
                 uid = None, cookies = None):
        self._session = requests.Session()
        if cookies:
            # check if we already have a cookie to authenticate our session with
            assert(uid and
                   isinstance(cookies, requests.cookies.RequestsCookieJar))
            self._session.cookies = cookies
            self._uid = uid
            """
             TODO: there could be a way to get uid from the API
             otherwise we'll have to store the mapping
             uid -> session cookie elsewhere
            """
        else:
            # otherwise run a post to get one
            assert(username and password)
            r = self._session.post('https://api.couchsurfing.org/sessions',
                              data={"username": username, "password": password})
            if (r.status_code != 200):
                raise AuthError
            self._uid = int(r.json()["url"].split('/')[-1])

    def get(self, *args, **kwargs):
        r = self._session.get(*args, **kwargs)
        if (r.status_code == 200):
            return r
        else:
            raise RequestError

    @property
    def uid(self):
        return self._uid

    @property
    def cookies(self):
        return self._session.cookies

if __name__ == "__main__":
    import doctest
    doctest.testmod()