"pyoauth2client is a library for writing oAuth2 client implementations"
from collections import namedtuple as _namedtuple
from abc import ABCMeta as _ABCMeta, abstractproperty as _abstractproperty, abstractmethod as _abstractmethod

class Response(metaclass = _ABCMeta):
    text = _abstractproperty(doc = "Content of the response, in unicode")
    status_code = _abstractproperty(doc = "Integer code of the responded HTTP Status")

_Request = _namedtuple("_Request", ("method", "url", "data", "headers", "cookies"))

class Request(_Request):
    def __new__(cls, method, url, data = {}, headers = {}, cookies = {}):
        return super().__new__(cls, method, url, data, headers, cookies)

def apply_query_to_url(p, url):
    """Applies a key-value query string to URL. """
    from urllib.parse import urlsplit, urlunsplit, urlencode
    x = urlsplit(url)
    if x.query == '':
        query = urlencode(p)
    else:
        query = '{}&{}'.format(x.query, urlencode(p))
    return urlunsplit((x[0], x[1], x[2], query, x[4]))

def apply_headers_to_req(headers, req):
    try:
        h = dict(req.headers)
    except:
        h = dict()
    h.update(headers)
    return req._replace(headers = h)

def apply_url_query_to_req(query, req):
    from urllib.parse import urlsplit, urlunsplit, urlencode
    try:
        url = str(req.url)
    except:
        url = ""
    x = urlsplit(url)
    if x.query == '':
        q = urlencode(query)
    else:
        q = '{}&{}'.format(x.query, urlencode(query))
    return req._replace(url = urlunsplit((x[0], x[1], x[2], q, x[4])))

def apply_data_to_req(data, req):
    try:
        d = dict(req.data)
    except:
        d = dict()
    d.update(data)
    return req._replace(method = "POST", data = d)


class Scope(frozenset):
    """A list of scopes."""
    def __new__(cls, iterable):
        #Handle special case of iterable is a string. We split at ' '.
        if isinstance(iterable, str):
            iterable = iterable.split(' ')
        return frozenset.__new__(cls, iterable) if iterable \
                else frozenset.__new__(cls)
    def join(self):
        return ' '.join(self)
    def __str__(self):
        return self.join()

class ClientCredentials(metaclass = _ABCMeta):
    id = _abstractproperty()
    apply_req = _abstractmethod(lambda cred, req: req)

class Grant(metaclass = _ABCMeta):
    apply_req = _abstractmethod(lambda grant, req: req)


class AccessToken(metaclass = _ABCMeta):
    scope = _abstractproperty(doc = "Scope of the access token, if provided")
    expires_in = _abstractproperty(doc = "The lifetime in seconds of the access token (Optional")
    client_id = _abstractproperty()
    apply_req = _abstractmethod(lambda token, req: req)

class Flow(metaclass = _ABCMeta):
    """Implementations of this abc provide an authorization flow which will
    return a TokenStore"""
    #token_store = _abstractmethod(lambda self: None)

class EndpointError(Exception):
    """Server endpoint returned an error"""
    def __init__(self, error, error_description = None, error_uri = None):
        self.error = error
        self.error_description = error_description
        self.error_uri = error_uri
    def __str__(self):
        return '(error = {0}, error_description = {1}, error_uri = {2})'.format(
                repr(self.error), repr(self.error_description), repr(self.error_uri))

class TokenStore:
    #TODO: Implement pickle protocol
    def __init__(self, server, access_token = None, refresh_token_grant = None, path = None):
        from .db import token_store_path
        self.server = server
        self.access_token = access_token
        self.refresh_token_grant = refresh_token_grant
        if path is None:
            self.path = token_store_path(server.name)
        else:
            self.path = path
        self.modified = True

    def loads(self, input):
        import pickle
        self.access_token, self.refresh_token_grant = pickle.loads(input)
        self.modified = False

    def load(self, file = None):
        import pickle
        if file is None:
            if self.path is not None:
                file = self.path
            else:
                raise ValueError("file must be provided if self.path is None")
        if isinstance(file, str):
            self.path = file 
            file = open(file, "rb")
        self.access_token, self.refresh_token_grant = pickle.load(file)
        self.modified = False

    def dumps(self):
        import pickle
        return pickle.dumps((self.access_token, self.refresh_token_grant))
    
    def dump(self, file = None):
        import pickle
        if file is None:
            if self.path is not None:
                file = self.path
            else:
                raise ValueError("file must be provided if self.path is None")
        if self.modified:
            if isinstance(file, str):
                self.path = file
                file = open(file, "wb")
            pickle.dump((self.access_token, self.refresh_token_grant), file)
            return True
        else:
            return False

    def refresh(self):
        y = self.server.token(self.refresh_token_grant)
        self.access_token = y.access_token
        if y.refresh_token_grant: self.refresh_token_grant = y.refresh_token_grant

    def apply_req(self, *args, **kwargs):
        return self.access_token.apply_req(*args, **kwargs)

    @property
    def can_refresh(self):
        return bool(self.refresh_token_grant)

    def __repr__(self):
        return '{}({!r}, {!r}, {!r}, {!r})'.format(self.__class__.__name__,
                self.server, self.access_token, self.refresh_token_grant,
                self.path)

class Server(metaclass = _ABCMeta):
    name = _abstractproperty(doc = "Name of the server")
    client_credential_types = _abstractproperty()

    def token_store(self):
        "Loads token store from db."
        from .db import token_store
        return token_store(self.name, self)
