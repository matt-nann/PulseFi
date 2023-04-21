import sys
import traceback
import datetime
from datetime import datetime, timedelta
from contextlib import contextmanager

import pandas as pd 
from fitbit.api import Fitbit
from fitbit.exceptions import HTTPTooManyRequests, HTTPUnauthorized
from flask import redirect, url_for, request, current_app
from flask_login import current_user
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError, MismatchingStateError, MissingTokenError

from src import getSecret, isRunningInCloud, FLASK_PORT, CLOUD_URL
from src.flaskServer.models import HeartRate

def refresh_cb(token_dict):
    print("Token refreshed: ", token_dict)

class FitbitClient(object):
    client_id = getSecret('FITBIT_CLIENT_ID')
    client_secret = getSecret('FITBIT_CLIENT_SECRET')
    def __init__(self, API):
        self.db = API.db
        self._TokenRefreshed = {}
    def __enter__(self):
        self.fitbit = Fitbit(self.client_id, self.client_secret, oauth2=True, 
                            refresh_cb=refresh_cb,
                            access_token=current_user.fitbit_access_token, refresh_token=current_user.fitbit_refresh_token)
        return self
    def __exit__(self, exception_type, exception_value, traceback):
        ...
    def updateClient(self):
        self.fitbit = Fitbit(self.client_id, self.client_secret, oauth2=True, access_token=current_user.fitbit_access_token, refresh_token=current_user.fitbit_refresh_token)
    def refreshToken(self):
        try:
            # print("Refreshing token, old access token: ", self.fitbit.client.session.token['access_token'])
            try:
                self.fitbit.client.refresh_token()
                current_user.fitbit_access_token = self.fitbit.client.session.token['access_token']
                self.db.session.commit()
            except InvalidGrantError:
                print("Invalid grant error need to reauthorize")
                current_user.fitbit_authorized = False
                current_user.fitbit_access_token = None
                current_user.fitbit_refresh_token = None
                self.db.session.commit()
        except Exception as e:
            print("Error refreshing token: ", e)
            raise
    def query(self, function, resource, *args, **kwargs):
        try:
            return getattr(self.fitbit, function)(resource, *args, **kwargs)
        except Exception as e:
            print("Error retrieving auth client: ", e, " type: ", type(e))
            if isinstance(e, InvalidGrantError):
                current_user.fitbit_authorized = False
                current_user.fitbit_access_token = None
                current_user.fitbit_refresh_token = None
                self.db.session.commit()
                return pd.DataFrame()
            if isinstance(e, HTTPTooManyRequests):
                print("Too many requests for fitbit data, retrying in ", int(e.retry_after_secs) / 60 , " minutes")
            if isinstance(e, HTTPUnauthorized):
                print("Unauthorized for fitbit data, refreshing token")
                self.refreshToken()
                if not current_user.fitbit_authorized:
                    return pd.DataFrame()
                self.updateClient()
                return getattr(self.fitbit, function)(resource, *args, **kwargs)
            print("Error retrieving auth client: ", e)
            raise

class Fitbit_API:
    """
        authorization flow
        anytime the user requests data from fitbit, the user is first checked to see if they are authorized
        if the user is unauthorized then they are redirected to fitbit's authorization page
        upon completion the user is redirected back to the app at /authorize, where the access token is retrieved
        lastly the user is redirected to the page they were on before the authorization flow
    """
    ALLOTED_AUTH_TIME = 20 # seconds
    def __init__(self, db):
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
        self.db = db

    def authorize(self):
        """
        
        """
        if not current_user.fitbit_authorized:
            url, _ = self.fitbit.client.authorize_token_url()
            return redirect(url)
        
    def saveHeartData(self, df_heartRate):
        latest_datetime = self.db.session.query(HeartRate.datetime).filter_by(user_id=current_user.id).order_by(HeartRate.datetime.desc()).first()
        if latest_datetime:
            latest_datetime = latest_datetime[0]
            df_new = df_heartRate[df_heartRate['datetime'] > latest_datetime]
        else:
            df_new = df_heartRate

        heartRateList = []
        for index, row in df_new.iterrows():
            heartRate = HeartRate(
                user_id=current_user.id,
                datetime=row['datetime'],
                bpm=row['bpm']
            )
            heartRateList.append(heartRate)
        self.db.session.add_all(heartRateList)

        self.db.session.commit()

    def heartRateData(self):
        # super old data
        # startTime = datetime.strptime('2022-07-03', '%Y-%m-%d')
        # endTime = datetime.strptime('2022-10-1', '%Y-%m-%d')
        latest_datetime = self.db.session.query(HeartRate.datetime).filter_by(user_id=current_user.id).order_by(HeartRate.datetime.desc()).first()
        if latest_datetime:
            startTime = latest_datetime[0]
        else:
            startTime = datetime.strptime('2023-04-01', '%Y-%m-%d')
        # startTime = datetime.now().date() - timedelta(days=1)
        # startTime = startTime.strftime("%Y-%m-%d")
        endTime = datetime.now().date().strftime("%Y-%m-%d") + ' 23:59:59'
        date_list = []
        df_list = []
        allDates = pd.date_range(start=startTime, end = endTime)
        for oneDate in allDates:
            oneDate = oneDate.date().strftime("%Y-%m-%d")
            with FitbitClient(self) as fitbit:
                # TODO KeyError: 'activities-heart-intraday' Error retrieving auth client:  (invalid_grant)   type:  <class 'oauthlib.oauth2.rfc6749.errors.InvalidGrantError'>
                oneDayData = fitbit.query('intraday_time_series', resource='activities/heart', base_date=oneDate, detail_level='1sec')
            df = pd.DataFrame(oneDayData['activities-heart-intraday']['dataset'])
            date_list.append(oneDate)
            df_list.append(df)

        final_df_list = []
        for date, df in zip(date_list, df_list):
            if len(df) == 0:
                continue
            df.loc[:, 'date'] = pd.to_datetime(date)
            final_df_list.append(df)
            # break
        if len(final_df_list):
            df_heartRate = pd.concat(final_df_list, axis = 0)
            df_heartRate['datetime'] = pd.to_datetime(df_heartRate['date']) + pd.to_timedelta(df_heartRate['time'])
            df_heartRate.rename(columns={'value':'bpm'}, inplace=True)
            self.saveHeartData(df_heartRate)
        else:
            df_heartRate = pd.DataFrame()

        latest_heart_rate_query = self.db.session.query(HeartRate).filter_by(user_id=current_user.id)
        df_heartRate_saved = pd.DataFrame([hr.__dict__ for hr in latest_heart_rate_query])
        df_heartRate_saved.drop(columns=['_sa_instance_state'], inplace=True)
        if not df_heartRate_saved.empty:
            df_heartRate = pd.concat([df_heartRate_saved, df_heartRate], axis = 0)
        
        df_heartRate = df_heartRate.sort_values(by='datetime')

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
            return df_heartRate.to_html()

        return app