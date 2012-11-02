"""A Basic Authorization Server definition.
Should cover 95% of the servers out there."""
from . import *
from .clientcredentials import ClientPasswordCredentials
from .grants import AuthorizationCodeGrant
from .tokens import BearerToken
from .endpoints import AuthorizationCodeEndpoint, TokenEndpoint, BasicFlow

class OAuth2Server(BasicFlow, Server):
    client_credential_types = {"password": ClientPasswordCredentials}
    client_credentials = None
    auth_endpoint = None
    token_endpoint = None
    def __init__(self, client_credentials = None, auth_endpoint = None, token_endpoint = None,
            scope = None, ua_modify_port = None, redirect_uri = None, 
            resources = None):
        from collections import Mapping
        if client_credentials:
            self.client_credentials = client_credentials
        elif not self.client_credentials:
            raise ValueError("client_credentials must be provided if " \
                    "self.client_credentials is None")
        if auth_endpoint:
            self.auth_endpoint = auth_endpoint
        elif not self.auth_endpoint:
            raise ValueError("auth_endpoint must be provided if " \
                    "self.auth_endpoint is None")
        if token_endpoint:
            self.token_endpoint = token_endpoint
        elif not self.token_endpoint:
            raise ValueError("token_endpoint must be provided if " \
                    "self.token_endpoint is None")
        if scope: self.scope = scope
        if ua_modify_port: self.ua_modify_port = ua_modify_port
        if redirect_uri: self.redirect_uri = redirect_uri
        if resources: self.resources = resources
    def __repr__(self):
        return '{}({!r}, {!r}, {!r})'.format(self.__class__.__name__,
                self.auth_endpoint, self.token_endpoint, self.client_credentials)

