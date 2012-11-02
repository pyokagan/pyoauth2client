"""Requests support library"""
import requests.auth

class OAuth2(requests.auth.AuthBase):
    def __init__(self, token_store):
        self.token_store = token_store
    def pre_send(self, x):
        from . import Request
        y = Request(x.method, x.url, x.data, x.headers, x.cookies)
        y = self.token_store.access_token.apply_req(y)
        x.method = y.method
        x.url = y.url
        x.data = y.data
        x.headers = y.headers
        x.cookies = y.cookies
        return x
    def response(self, x):
        import requests
        if x.status_code != 200:
            if self.token_store.can_refresh:
                try:
                    self.token_store.refresh()
                except EndpointError:
                    return
                #Remove hook to prevent infinite loop
                x.request.deregister_hook("response", self.response)
                x.request.send(anyway = True)
            return x.request.response
    def __call__(self, r):
        r.register_hook("pre_send", self.pre_send)
        r.register_hook("response", self.response)
        return r





