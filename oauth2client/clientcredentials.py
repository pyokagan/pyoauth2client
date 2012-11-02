"""
Client Credentials
"""
from . import *
from collections import namedtuple as _namedtuple

_ClientPasswordCredentials = _namedtuple("_ClientPasswordCredentials", ("id", "secret"))

class ClientPasswordCredentials(_ClientPasswordCredentials, ClientCredentials):
    def apply_req_headers(cred, req):
        from base64 import b64encode
        cred = '{0}:{1}'.format(cred.id, cred.secret)
        encoded_cred = b64encode(cred.encode('ascii')).decode('ascii')
        return apply_headers_to_req({"Authorization": "Basic {0}".format(encoded_cred)}, req)

    def apply_req_data(cred, req):
        q = {"client_id": cred.id, "client_secret": cred.secret}
        return apply_data_to_req(q, req)

    def apply_req_urlquery(cred, req):
        q = {"client_id": cred.id, "client_secret": cred.secret}
        return apply_url_query_to_req(q, req)

    #NOTE: Ideally, this should be apply_req_headers as oauth2 spec requires
    #apply_req_headers. However, most servers only support apply_req_data
    apply_req = apply_req_data
