# Copyright 2017 Zegami Ltd

"""API client for talking to Zegami cloud version."""

from __future__ import absolute_import

from . import (
    http,
)


class AuthClient(object):
    """HTTP client for interacting with the Zegami api."""

    def __init__(self, oauth_url):
        """Initialise client."""
        self.oauth_url = oauth_url
        self.session = http.make_session()

    def get_user_token(self, username, password):
        """Authenticate user and get token."""
        info = {"username": username, "password": password}
        token = None
        try:
            response_json = http.post_json(self.session, self.oauth_url, info)
            token = response_json.get('token')
        except:
            pass
        return token
