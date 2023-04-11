# gather_keys_oauth2.py file needs to be in the same directory. 
# also needs to install cherrypy: https://pypi.org/project/CherryPy/
import pandas as pd 
import datetime
from datetime import datetime, timedelta
from fitbit.api import Fitbit
from flask import has_request_context, redirect, url_for
import requests
import traceback
from flask import request
from oauthlib.oauth2.rfc6749.errors import MismatchingStateError, MissingTokenError

from .gather_keys_oauth2 import OAuth2Server
from __init__ import getSecret


import cherrypy
import os
import sys
import threading
import traceback
import webbrowser
import time

from urllib.parse import urlparse
from base64 import b64encode
from fitbit.api import Fitbit
from oauthlib.oauth2.rfc6749.errors import MismatchingStateError, MissingTokenError
from __init__ import getSecret, isRunningInCloud, FLASK_PORT

class FitbitAuth:
    ALLOTED_AUTH_TIME = 20 # seconds
    def __init__(self):
        self.client_id = getSecret('FITBIT_CLIENT_ID')
        self.client_secret = getSecret('FITBIT_CLIENT_SECRET')

        # self.server = OAuth2Server() 
        self.unauthorized = True
        self.failedAuth = False
        self.auth2_client = None

        # client_id = getSecret('FITBIT_CLIENT_ID')
        # client_secret = getSecret('FITBIT_CLIENT_SECRET')
        if isRunningInCloud():
            redirect_uri = 'https://pulse-fi.herokuapp.com/authorize'
        else:
            redirect_uri ='http://127.0.0.1:'+str(FLASK_PORT)+'/authorize'
        
        """ Initialize the FitbitOauth2Client """
        self.success_html = """
            <h1>You are now authorized to access the Fitbit API!</h1>
            <br/><h3>You can close this window</h3>"""
        self.failure_html = """
            <h1>ERROR: %s</h1><br/><h3>You can close this window</h3>%s"""

        self.fitbit = Fitbit(
            self.client_id,
            self.client_secret,
            redirect_uri=redirect_uri,
            timeout=100,
        )
        self.redirect_uri = redirect_uri

    def authorize(self):
        if self.failedAuth:
            return 'Failed to authorize Fitbit'
        if self.unauthorized:
            url, _ = self.fitbit.client.authorize_token_url()  # Add the state parameter to the URL
            return redirect(url)
    
    def requestMultipleDays(self):
        startTime = datetime.strptime('2022-07-03', '%Y-%m-%d')
        endTime = datetime.strptime('2022-10-31', '%Y-%m-%d')
        endTime = datetime.now().date().strftime("%Y-%m-%d")
        startTime = (datetime.now() - timedelta(days=1)).date().strftime("%Y-%m-%d")
        date_list = []
        df_list = []
        allDates = pd.date_range(start=startTime, end = endTime)
        for oneDate in allDates:
            oneDate = oneDate.date().strftime("%Y-%m-%d")
            oneDayData = self.auth2_client.intraday_time_series('activities/heart', base_date=oneDate, detail_level='1sec')
            df = pd.DataFrame(oneDayData['activities-heart-intraday']['dataset'])
            date_list.append(oneDate)
            df_list.append(df)
            
        final_df_list = []
        for date, df in zip(date_list, df_list):
            if len(df) == 0:
                continue
            df.loc[:, 'date'] = pd.to_datetime(date)
            final_df_list.append(df)

        df_heartRate = pd.concat(final_df_list, axis = 0)
        df_heartRate['datetime'] = pd.to_datetime(df_heartRate['date']) +pd.to_timedelta(df_heartRate['time'])
        return df_heartRate

    def _fmt_failure(self, message):
        tb = traceback.format_tb(sys.exc_info()[2])
        tb_html = '<pre>%s</pre>' % ('\n'.join(tb)) if tb else ''
        return self.failure_html % (message, tb_html)
    
    def add_routes(self, app):

        @app.route('/authorize', methods=['GET','POST'])
        def fitbit_auth():
            code = request.args.get('code')
            error = request.args.get('error')
            print("fitbit_auth", code, error)
            """
            Receive a Fitbit response containing a verification code. Use the code
            to fetch the access_token.
            """
            error = None
            if code:
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
            if error:
                return error
            else:
                self.ACCESS_TOKEN=str(self.fitbit.client.session.token['access_token'])
                self.REFRESH_TOKEN=str(self.fitbit.client.session.token['refresh_token'])
                self.unauthorized = False
                self.auth2_client=Fitbit(self.client_id,self.client_secret,oauth2=True,access_token=self.ACCESS_TOKEN,refresh_token=self.REFRESH_TOKEN)
                return redirect(url_for('heartRate'))

        @app.route('/heartRate', methods=['GET'])
        def heartRate():
            page = self.authorize()
            if page:
                return page
            
            df_heartRate = self.requestMultipleDays()

            # Define the layout of the app
            # app.layout = html.Div([
            #     dcc.Graph(id='my-graph'),
            #     dcc.Dropdown(
            #         id='column-dropdown',
            #         options=[{'label': col, 'value': col} for col in df.columns],
            #         value=df.columns[0]
            #     )
            # ])
            # to html
            return df_heartRate.to_html()

        # import random
        # @app.url_defaults
        # def add_random_number(endpoint, values):
        #     if endpoint == 'heartRate':
        #         values.setdefault('random', str(random.randint(0, 999999)))
        # @app.after_request
        # def add_header(response):
        #     if request.path == '/heartRate':
        #         response.headers['Cache-Control'] = 'no-store'
        #     return response
        # @app.url_defaults
        # def add_random_number(endpoint, values):
        #     if endpoint == 'heartRate':
        #         values.setdefault('random', str(random.randint(0, 999999))
        # @app.url_value_preprocessor
        # def check_random_number(endpoint, values):
        #     if endpoint == 'heartRate':
        #         if 'random' not in values:
        #             return 'Invalid request', 400
        # app.register_blueprint(heart_rate_bp, lazy_load=True)

        return app