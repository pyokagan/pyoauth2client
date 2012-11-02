"""
Google's version of oAuth
"""
from .baseserver import *

_scope= """
https://www.googleapis.com/auth/adsense
https://www.googleapis.com/auth/gan
https://www.googleapis.com/auth/analytics.readonly
https://www.googleapis.com/auth/books
https://www.googleapis.com/auth/blogger
https://www.googleapis.com/auth/calendar
https://www.googleapis.com/auth/devstorage.read_write
https://www.google.com/m8/feeds/
https://www.googleapis.com/auth/structuredcontent
https://www.googleapis.com/auth/chromewebstore.readonly
https://docs.google.com/feeds/
https://www.googleapis.com/auth/drive
https://mail.google.com/mail/feed/atom
https://www.googleapis.com/auth/plus.me
https://apps-apis.google.com/a/feeds/groups/
https://www.googleapis.com/auth/latitude.all.best
https://www.googleapis.com/auth/latitude.all.city
https://www.googleapis.com/auth/moderator
https://apps-apis.google.com/a/feeds/alias/
https://www.googleapis.com/auth/orkut
https://picasaweb.google.com/data/
https://sites.google.com/feeds/
https://spreadsheets.google.com/feeds/
https://www.googleapis.com/auth/tasks
https://www.googleapis.com/auth/urlshortener
https://www.googleapis.com/auth/userinfo.email
https://www.googleapis.com/auth/userinfo.profile
https://apps-apis.google.com/a/feeds/user/
https://www.google.com/webmasters/tools/feeds/
https://gdata.youtube.com""".split("\n")

class GoogleOAuth2(OAuth2Server):
    name = "google"
    auth_endpoint = "https://accounts.google.com/o/oauth2/auth"
    token_endpoint = "https://accounts.google.com/o/oauth2/token"
    #redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
    redirect_uri = "http://localhost"
    scope = Scope([x.strip() for x in _scope if x.strip()])
