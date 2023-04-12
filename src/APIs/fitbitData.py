import sys
import traceback
import datetime
from datetime import datetime, timedelta

import pandas as pd 
from fitbit.api import Fitbit
from flask import redirect, url_for, request
from flask_login import current_user
from oauthlib.oauth2.rfc6749.errors import MismatchingStateError, MissingTokenError

from src import getSecret, isRunningInCloud, FLASK_PORT, CLOUD_URL

class Fitbit_API:
    """
        authorization flow
        anytime the user requests data from fitbit, the user is first checked to see if they are authorized
        if the user is unauthorized then they are redirected to fitbit's authorization page
        upon completion the user is redirected back to the app at /authorize, where the access token is retrieved
        lastly the user is redirected to the page they were on before the authorization flow
    """
    ALLOTED_AUTH_TIME = 20 # seconds
    def __init__(self):
        self.client_id = getSecret('FITBIT_CLIENT_ID')
        self.client_secret = getSecret('FITBIT_CLIENT_SECRET')

        if isRunningInCloud():
            redirect_uri = CLOUD_URL + '/authorize_fitbit'
        else:
            redirect_uri = 'http://127.0.0.1:'+str(FLASK_PORT)+'/authorize_fitbit'
        
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
        """
        
        """
        if not current_user.fitbit_authorized:
            url, _ = self.fitbit.client.authorize_token_url()
            return redirect(url)
        
    def retrieveAuthClient(self):
        return Fitbit(self.client_id,self.client_secret,oauth2=True,access_token=current_user.fitbit_access_token,refresh_token=current_user.fitbit_refresh_token)

    def heartRateData(self):
        startTime = datetime.strptime('2022-07-03', '%Y-%m-%d')
        endTime = datetime.strptime('2022-10-31', '%Y-%m-%d')
        endTime = datetime.now().date().strftime("%Y-%m-%d")
        startTime = (datetime.now() - timedelta(days=1)).date().strftime("%Y-%m-%d")
        date_list = []
        df_list = []
        allDates = pd.date_range(start=startTime, end = endTime)
        for oneDate in allDates:
            oneDate = oneDate.date().strftime("%Y-%m-%d")
            oneDayData = self.retrieveAuthClient().intraday_time_series('activities/heart', base_date=oneDate, detail_level='1sec')
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
        df_heartRate.rename(columns={'value':'bpm'}, inplace=True)
        return df_heartRate

    def _fmt_failure(self, message):
        tb = traceback.format_tb(sys.exc_info()[2])
        tb_html = '<pre>%s</pre>' % ('\n'.join(tb)) if tb else ''
        return self.failure_html % (message, tb_html)
    
    def add_routes(self, app, db, spotify_and_fitbit_authorized_required):

        @app.route('/authorize_fitbit', methods=['GET','POST'])
        def authorize_fitbit():
            code = request.args.get('code')
            error = request.args.get('error')
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
                ACCESS_TOKEN=str(self.fitbit.client.session.token['access_token'])
                REFRESH_TOKEN=str(self.fitbit.client.session.token['refresh_token'])
                current_user.fitbit_authorized = True
                current_user.fitbit_access_token = ACCESS_TOKEN
                current_user.fitbit_refresh_token = REFRESH_TOKEN
                db.session.commit()
                return redirect(url_for('home'))
            
        @app.route('/user_authorize_fitbit', methods=['GET'])
        def user_authorize_fitbit():
            page = self.authorize()
            if page:
                return page
            return redirect(url_for('home'))

        @app.route('/heartRate', methods=['GET'])
        @spotify_and_fitbit_authorized_required
        def heartRate():
            df_heartRate = self.heartRateData()
            return df_heartRate.to_dict(orient='records')

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