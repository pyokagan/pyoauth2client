"""
oauth2 authentication server database

Note that this module should only be used for generic tools.
(e.g. the command line oauth tool)
If you are using Python, just import the respective
module directly!
"""
import sys

base_db = {
    "github": {
        "_oauth2client.import": "oauth2client.github.GithubOAuth2",
        "resources": r"https://api\.github\.com"
    },
    "google": {
        "_oauth2client.import": "oauth2client.google.GoogleOAuth2",
        "resources": r"https://www\.googleapis\.com/auth/adsense|" \
                r"https://www\.googleapis\.com/auth/gan|" \
                r"https://www\.googleapis\.com/auth/analytics\.readonly|"\
                r"https://www\.googleapis\.com/auth/books|" \
                r"https://www\.googleapis\.com/auth/blogger|" \
                r"https://www\.googleapis\.com/auth/calendar|" \
                r"https://www\.googleapis\.com/auth/devstorage\.read_write|" \
                r"https://www\.google\.com/m8/feeds/|" \
                "https://www\.googleapis\.com/auth/structuredcontent|" \
                "https://www\.googleapis\.com/auth/chromewebstore\.readonly|" \
                "https://docs\.google\.com/feeds/|" \
                "https://www\.googleapis\.com/auth/drive\.file|" \
                "https://mail\.google\.com/mail/feed/atom|" \
                "https://www\.googleapis\.com/auth/plus\.me|" \
                "https://apps-apis\.google\.com/a/feeds/groups/|" \
                "https://www\.googleapis\.com/auth/latitude\.all\.best|" \
                "https://www\.googleapis\.com/auth/latitude\.all\.city|" \
                "https://www\.googleapis\.com/auth/moderator|" \
                "https://apps-apis\.google\.com/a/feeds/alias/|" \
                "https://www\.googleapis\.com/auth/orkut|" \
                "https://picasaweb\.google\.com/data/|" \
                "https://sites\.google\.com/feeds/|" \
                "https://spreadsheets\.google\.com/feeds/|" \
                "https://www\.googleapis\.com/auth/tasks|" \
                "https://www\.googleapis\.com/auth/urlshortener|" \
                "https://www\.googleapis\.com/auth/userinfo\.email|" \
                "https://www\.googleapis\.com/auth/userinfo\.profile|" \
                "https://apps-apis\.google\.com/a/feeds/user/|" \
                "https://www\.google\.com/webmasters/tools/feeds/|" \
                "https://gdata\.youtube\.com|" \
                "https://www\.googleapis\.com/oauth2"
    },
    "facebook": {
        "_oauth2client.import": "oauth2client.facebook.FacebookOAuth2",
        "resources": r"https://graph\.facebook\.com"
    }
}

def get_all_file_paths_in_path(path:str):
    """Return a list of all paths in the directory `path`"""
    """path: Path. Returns: TypedIterator(Path)"""
    from os import walk
    from os.path import join, relpath
    from itertools import chain
    def join_paths(dir_path, filenames):
        return (join(path, join(dir_path, filename)) for \
                filename in filenames)
    files_iter = (join_paths(dir_path, filenames) for \
            dir_path, _, filenames in walk(path))
    return chain.from_iterable(files_iter)

def get_all_file_paths_in_paths(paths):
    """Return a list of all paths in the list of paths"""
    """path: TypedIteratore(Path). Returns: TypedIterator(Path)"""
    from os.path import isfile, isdir
    from itertools import chain
    def handle(x):
        if isdir(x):
            return get_all_file_paths_in_path(x)
        elif isfile(x):
            return [x]
        else:
            return None
    paths_iter = (handle(x) for x in paths)
    paths_iter2 = filter(None, paths_iter)
    return chain.from_iterable(paths_iter2)

def _gen_windows_config_search_paths():
	from os.path import join
	from os import getenv
	x = getenv('ProgramFiles', 'C:\\Program Files')
	y = getenv('APPDATA')
	return [
		join(x, 'oauth2.d'),
		join(x, 'oauth2.json'),
		join(y, 'oauth2/oauth2.d'),
		join(y, 'oauth2/oauth2.json')
		]
def _gen_posix_config_search_paths():
    from os.path import expanduser
    return [
        '/usr/share/oauth2/oauth2.d',
        '/usr/share/oauth2/oauth2.json',
        '/usr/local/share/oauth2/oauth2.d',
        '/usr/local/share/oauth2/oauth2.json',
        '/etc/oauth2.json',
        expanduser('~/.local/share/oauth2/oauth2.d'),
        expanduser('~/.local/share/oauth2/oauth2.json'),
        expanduser('~/.config/oauth2.json')
        ]


if sys.platform == 'win32':
    config_search_paths = _gen_windows_config_search_paths()
else:
    config_search_paths = _gen_posix_config_search_paths()

def merge(x, y):
    from copy import deepcopy
    #x = deepcopy(x)
    for key in x:
        if key in y:
            x[key].update(y[key])
    return x

def load_config(paths = config_search_paths):
    import json
    from functools import reduce
    from itertools import chain
    z = get_all_file_paths_in_paths(paths)
    def load_file(x):
        f = open(x, "r", encoding = 'utf-8')
        y = json.load(f)
        f.close()
        return y
    configs = (load_file(x) for x in z)
    return reduce(lambda x, y: merge(x, y), chain([base_db], configs)) 

def _server(x):
    """Parses a JSON configuration section"""
    from copy import deepcopy
    x = deepcopy(x)
    if "_oauth2client.import" in x:
        module, _, cls = x["_oauth2client.import"].rpartition(".")
        module = __import__(module, fromlist = [cls])
        cls = getattr(module, cls)
        del x["_oauth2client.import"]
    else:
        from .baseserver import BaseServer
        cls = BaseServer
    if "client_credentials" in x:
        client_credentials = x["client_credentials"]
        if "type" in client_credentials:
            client_type = client_credentials["type"]
            del client_credentials["type"]
        else:
            client_type = "password"
        client_credentials = cls.client_credential_types[client_type](**client_credentials)
        del x["client_credentials"]
    else:
        client_credentials = None
    y = dict((k, v) for k, v in x.items() if not k.startswith("_"))
    srv = cls(client_credentials = client_credentials, **y)
    return srv

def server(x, paths = config_search_paths):
    return _server(load_config(paths)[x])

def _gen_posix_token_store_path(name):
    from os.path import expanduser
    return expanduser("~/.local/share/oauth2/tokens/{}".format(name))

def token_store_path(name):
    return _gen_posix_token_store_path(name)

def token_store(name, srv = None):
    #If server is None, will load using the server() function
    from . import TokenStore
    path = token_store_path(name)
    if srv is None:
        srv = server(name)
    x = TokenStore(srv)
    x.load(path)
    return x

def url(x, paths = config_search_paths):
    """Returns the server which has a resource under URL"""
    import re
    servers = (_server(v) for v in load_config(paths).values() \
            if "resources" in v and re.match(v["resources"], x))
    return next(servers, None)
