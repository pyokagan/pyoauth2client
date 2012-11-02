from . import *
from collections import namedtuple as _namedtuple
from abc import ABCMeta as _ABCMeta, abstractproperty as _abstractproperty, abstractmethod as _abstractmethod
from http.server import BaseHTTPRequestHandler, HTTPServer

"""The Endpoints"""

class AuthorizationEndpoint(metaclass = _ABCMeta):
    auth_endpoint = _abstractproperty()

    AuthorizationContext = _namedtuple("AuthorizationContext",
        ("client_id", "redirect_uri", "scope", "state"))

    def auth_user_req(self, response_type, redirect_uri = None, 
            scope = None, state = None):
        from collections import Iterable
        if hasattr(self, "client_credentials"):
            client_id = self.client_credentials.id
        else:
            client_id = self.client_id
        if scope is None and hasattr(self, "scope"):
            scope = self.scope
        if redirect_uri is None:
            if hasattr(self, "auth_redirect_uri"):
                redirect_uri = self.auth_redirect_uri
            elif hasattr(self, "redirect_uri"):
                redirect_uri = self.redirect_uri
        p = {"client_id": client_id, "response_type": response_type}
        if redirect_uri: p["redirect_uri"] = redirect_uri
        if scope: p["scope"] = str(scope)
        if state: p["state"] = str(state)
        return (apply_query_to_url(p, self.auth_endpoint),
                self.AuthorizationContext(client_id, redirect_uri, scope, state))

class AuthorizationCodeEndpoint(AuthorizationEndpoint):
    from .grants import AuthorizationCodeGrant

    def auth_code_user_req(self, redirect_uri = None, scope = None, state = None):
        return self.auth_user_req("code", redirect_uri, scope, state)

    def auth_code_resp2grant(self, context, url):
        #TODO: perform state check
        from urllib.parse import urlsplit, parse_qs
        code = parse_qs(urlsplit(url).query)["code"][0]
        return self.AuthorizationCodeGrant(code = code, scope = context.scope,
                redirect_uri = context.redirect_uri)

    #Interactive version, utilising a web server and stuff
    #TODO: Allow user to set user interaction handler
    def auth_code(self, redirect_uri = None, scope = None, handler = None, modify_port = None):
        from . import ui
        if handler is None:
            handler = ui.ua_handler
        if redirect_uri is None:
            if hasattr(self, "auth_redirect_uri"):
                redirect_uri = self.auth_redirect_uri
            elif hasattr(self, "redirect_uri"):
                redirect_uri = self.redirect_uri
        if modify_port is None:
            if hasattr(self, "ua_modify_port"):
                modify_port = self.ua_modify_port
            else:
                modify_port = True
        def gen_req(redirect_uri):
            return self.auth_code_user_req(redirect_uri = redirect_uri, scope = scope)
        url, context = handler(gen_req, redirect_uri, modify_port = modify_port)
        return self.auth_code_resp2grant(context, url)

class TokenEndpoint(metaclass = _ABCMeta):
    from .tokens import BearerToken
    from .grants import RefreshTokenGrant
    token_endpoint = _abstractproperty()
    token_types = {"bearer": BearerToken}

    class TokenError(EndpointError):
        pass

    TokenResponse = _namedtuple("TokenResponse", ("access_token", "refresh_token_grant"))

    def token_client_req(self, grant):
        client = self.client_credentials
        #NOTE: Accept: application/json makes github work
        return client.apply_req(
                grant.apply_req(
                    Request("GET", self.token_endpoint, headers = {"Accept": "application/json"})))

    def parse_refresh_token_response(self, x):
        if "refresh_token" in x:
            return self.RefreshTokenGrant(
                x["refresh_token"], 
                x["scope"] if "scope" in x else None
                )
        else:
            return None

    def token_resp2token(self, resp):
        from json import loads
        r = loads(resp.text)
        if "error" in r:
            error = r["error"]
            error_description = r["error_description"] if "error_description" in r else None
            error_uri = r["error_uri"] if "error_uri" in r else None
            raise self.TokenError(error, error_description, error_uri)
        elif r["token_type"].lower() in self.token_types:
            token_type = self.token_types[r["token_type"].lower()].parse_token_response
            return self.TokenResponse(token_type(r), 
                    self.parse_refresh_token_response(r))
        else:
            raise Exception('Unsupported Token Type {}'.format(
                repr(r['token_type'])))

    def token(self, grant):
        import requests
        req = self.token_client_req(grant)
        r = requests.request(**(req._asdict()))
        return self.token_resp2token(r)

class BasicFlow(Flow, AuthorizationCodeEndpoint, TokenEndpoint):
    def basic_flow(self, redirect_uri = None, scope = None):
        from . import TokenStore
        g = self.auth_code(redirect_uri = redirect_uri, scope = scope)
        t = self.token(g)
        return TokenStore(self, t.access_token, t.refresh_token_grant)
