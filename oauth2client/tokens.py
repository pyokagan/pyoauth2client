from . import *
from collections import namedtuple as _namedtuple


_BearerToken = _namedtuple("BearerToken", ("data", "scope", "expires_in"))

class BearerToken(_BearerToken, AccessToken):
    def __new__(cls, data, scope = None, expires_in = None):
        return super().__new__(cls, data, scope, expires_in)

    def apply_req_header(token, req):
        return apply_headers_to_req({"Authorization": "Bearer {}".format(token.data)}, req)

    def apply_req_query(token, req):
        return apply_url_query_to_req({"access_token": token.data}, req)

    apply_req = apply_req_header

    def parse_token_response(x):
        """Parses a response and returns Bearer Token."""
        return BearerToken(
            data = x['access_token'], 
            scope = x["scope"] if "scope" in x else None,
            expires_in = x["expires_in"] if "expires_in" in x else None)

