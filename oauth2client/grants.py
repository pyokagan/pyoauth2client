from . import *
from collections import namedtuple as _namedtuple

_AuthorizationCodeGrant = _namedtuple("AuthorizationCodeGrant", ("code", "scope", "redirect_uri"))
#Redirect_uri (Needed to be provided for token endpoint)

class AuthorizationCodeGrant(_AuthorizationCodeGrant, Grant):
    def __new__(cls, code, scope, redirect_uri):
        assert(isinstance(scope, Scope))
        return super().__new__(cls, code, scope, redirect_uri)

    def apply_req_data(grant, req):
        p = {"grant_type": "authorization_code", "code": str(grant.code)}
        if grant.redirect_uri: p["redirect_uri"] = str(grant.redirect_uri)
        return apply_data_to_req(p, req)

    def apply_req_urlquery(grant, req):
        p = {"code": str(grant.code)}
        if grant.redirect_uri: p["redirect_uri"] = str(grant.redirect_uri)
        return apply_url_query_to_req(p, req)

    apply_req = apply_req_data

_RefreshTokenGrant = _namedtuple("RefreshTokenGrant", ("refresh_token", "scope"))

class RefreshTokenGrant(_RefreshTokenGrant, Grant):
    def __new__(cls, refresh_token, scope = None):
        return super().__new__(cls, refresh_token, scope)

    def apply_req_data(grant, req):
        p = {"grant_type": "refresh_token", "refresh_token": str(grant.refresh_token)}
        if grant.scope: p["scope"] = str(grant.scope)
        return apply_data_to_req(p, req)

    apply_req = apply_req_data

