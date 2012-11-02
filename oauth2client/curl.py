"""curl support library"""
class CurlWrapper:
    def __init__(self, token_store):
        self.token_store = token_store

    @staticmethod
    def req_to_curl_args(req):
        #Reconstruct CURL Request
        args = []
        #Headers
        if req.headers:
            for x, y in req.headers.items():
                args.append("-H")
                args.append("{}: {}".format(x, y))
        #Data
        if req.data:
            for x, y in req.data.items():
                args.append("-d")
                args.append(urlencode({x: y}))
        #Finally, URL
        args.append(req.url)
        return args

    def call_curl(self, req, args, refresh = True):
        from subprocess import call
        if self.token_store:
            r = self.token_store.apply_req(req)
        else:
            r = req
        return_code = call(["curl"] + self.req_to_curl_args(r) + ["-f"] + args)
        if return_code == 22 and self.token_store and \
                self.token_store.can_refresh and refresh:
            try:
                self.token_store.refresh()
            except EndpointError as e:
                return
            return self.call_curl(req, args, refresh = False)
        return return_code

    def main(self, args = None):
        from . import Request
        from argparse import ArgumentParser
        import sys
        p = ArgumentParser()
        args, rest = p.parse_known_args(args)
        if not rest:
            p.error("URL not specified")
        url = rest[-1]
        del rest[-1]
        req = Request(method = "GET", url = url, data = {}, headers = {}, cookies = {})
        return self.call_curl(req, rest)

