# https://github.com/orcasgit/python-fitbit/blob/master/gather_keys_oauth2.py
# This file implements a small local web server that you can use to authenticate with the Fitbit API to request an access and refresh token.
#!/usr/bin/env python
import cherrypy
import os
import sys
import threading
import traceback
import webbrowser

from urllib.parse import urlparse
from base64 import b64encode
from fitbit.api import Fitbit
from oauthlib.oauth2.rfc6749.errors import MismatchingStateError, MissingTokenError
from .. import getSecret

class OAuth2Server:
    def __init__(self,):
        client_id = getSecret('FITBIT_CLIENT_ID')
        client_secret = getSecret('FITBIT_CLIENT_SECRET')
        redirect_uri='http://127.0.0.1:8090/'
        """ Initialize the FitbitOauth2Client """
        self.success_html = """
            <h1>You are now authorized to access the Fitbit API!</h1>
            <br/><h3>You can close this window</h3>"""
        self.failure_html = """
            <h1>ERROR: %s</h1><br/><h3>You can close this window</h3>%s"""

        self.fitbit = Fitbit(
            client_id,
            client_secret,
            redirect_uri=redirect_uri,
            timeout=100,
        )
        self.redirect_uri = redirect_uri

    def browser_authorize(self):
        """
        Open a browser to the authorization url and spool up a CherryPy
        server to accept the response
        """
        url, _ = self.fitbit.client.authorize_token_url()
        print('Opening browser to: %s' % url)
        # Open the web browser in a new thread for command-line browser support
        threading.Timer(1, webbrowser.open, args=(url,)).start()

        # Same with redirect_uri hostname and port.
        urlparams = urlparse(self.redirect_uri)
        cherrypy.config.update({'server.socket_host': urlparams.hostname,
                                'server.socket_port': urlparams.port})
        cherrypy.quickstart(self)

    @cherrypy.expose
    def index(self, state=None, code=None, error=None):
        # print('state: %s' % state, 'code: %s' % code, 'error: %s' % error)
        """
        Receive a Fitbit response containing a verification code. Use the code
        to fetch the access_token.
        """
        error = None
        if code:
            # print('Received code: %s' % code)
            try:
                self.fitbit.client.fetch_access_token(code)
            except MissingTokenError:
                error = self._fmt_failure(
                    'Missing access token parameter.</br>Please check that '
                    'you are using the correct client_secret')
            except MismatchingStateError:
                error = self._fmt_failure('CSRF Warning! Mismatching state')
        else:
            error = self._fmt_failure('Unknown error while authenticating')
        # Use a thread to shutdown cherrypy so we can return HTML first
        self._shutdown_cherrypy()
        if error:
            return error
        return self.success_html

    def _fmt_failure(self, message):
        tb = traceback.format_tb(sys.exc_info()[2])
        tb_html = '<pre>%s</pre>' % ('\n'.join(tb)) if tb else ''
        return self.failure_html % (message, tb_html)

    def _shutdown_cherrypy(self):
        """ Shutdown cherrypy in one second, if it's running """
        # if cherrypy.engine.state == cherrypy.engine.states.STARTED:
        threading.Timer(1, cherrypy.engine.exit).start()