"""Github's version of OAuth"""
from .baseserver import *

class GithubOAuth2(OAuth2Server):
    name = "github"
    scope = Scope(["user", "public_repo", "repo", "gist"])
    auth_endpoint = "https://github.com/login/oauth/authorize"
    token_endpoint = "https://github.com/login/oauth/access_token"
    ua_modify_port = False
