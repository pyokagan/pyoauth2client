=======================================================
pyoauth2client: The intelligent oauth2 client library
=======================================================

oAuth2 is a big mess. pyoauth2client aims to make it 
easy to use.

Usage (Installed Applications)
================================
Using oauth2client.db
------------------------
Client Credentials will be read from `~/.config/oauth2.json`,
which is useful for installed applications.

With requests::

    >>> from oauth2client import db
    >>> token = db.server("google").basic_flow() 
    >>> from oauth2client.requests import OAuth2 
    >>> import requests
    >>> requests.get("https://www.googleapis.com/oauth2/v1/userinfo", auth = OAuth2(token)).json

Manual
-------
No configuration files will be read. Useful when you want
to implement your own configuration mechanism.

With requests::

    >>> from oauth2client.google import ClientPasswordCredentials, GoogleOAuth2
    >>> cred = ClientPasswordCredentials(id = "381049194886.apps.googleusercontent.com", secret = "msQUzuyt9zB9jyjBYhG7bV4L")
    >>> server = GoogleOAuth2(cred)
    >>> token = server.basic_flow()
    >>> from oauth2client.requests import OAuth2
    >>> import requests
    >>> requests.get("https://www.googleapis.com/oauth2/v1/userinfo", auth = OAuth2(token)).json


Usage (Web Server)
====================

To be written.

The oauth2.json configuration file
====================================
The `~/.config/oauth2.json` file contains your client
credentials. This file will be read when you load
a server with `db.server("SERVERNAME")`::

    {
        "github": {
            "client_credentials": {
                "id": "CLIENT ID",
                "secret": "CLIENT SECRET"
                },
            "redirect_uri": "REDIRECT URI (github requires it to be the same as your application settings)"
        },
        "google": {
            "client_credentials": {
                "id": "CLIENT ID",
                "secret": "CLIENT SECRET"
            }
        },
        "facebook": {
            "client_credentials": {
                "id": "CLIENT ID",
                "secret": "CLIENT SECRET"
            }
        }
    }

Features
==========

* Implements workarounds for non-conformnant authorization servers (See `oauth2client.facebook` for an example)


Authorization Server support
===============================

* Github
* Facebook
* Google

Specification Implementation
===============================
To be written.
