# gather_keys_oauth2.py file needs to be in the same directory. 
# also needs to install cherrypy: https://pypi.org/project/CherryPy/
import pandas as pd 
import datetime
from datetime import datetime, timedelta
from fitbit.api import Fitbit
from flask import has_request_context

from .gather_keys_oauth2 import OAuth2Server
from __init__ import getSecret

class FitbitAuth: #OAuth2Server
    def __init__(self):
        self.client_id = getSecret('FITBIT_CLIENT_ID')
        self.client_secret = getSecret('FITBIT_CLIENT_SECRET')

        self.server = OAuth2Server() 
        self.unauthorized = True
        self.auth2_client = None
    
    def retrieve_OAuth_FitBit_Tokens(self):
        if has_request_context():
            self.server.browser_authorize()
            ACCESS_TOKEN=str(self.server.fitbit.client.session.token['access_token'])
            REFRESH_TOKEN=str(self.server.fitbit.client.session.token['refresh_token'])
            return ACCESS_TOKEN, REFRESH_TOKEN

    def authorize(self):
        if self.unauthorized:
            self.ACCESS_TOKEN, self.REFRESH_TOKEN = self.retrieve_OAuth_FitBit_Tokens()
            self.unauthorized = False
            self.auth2_client=Fitbit(self.client_id,self.client_secret,oauth2=True,access_token=self.ACCESS_TOKEN,refresh_token=self.REFRESH_TOKEN)

    def requestMultipleDays(self):
        self.authorize()

        startTime = datetime.strptime('2022-07-03', '%Y-%m-%d')
        endTime = datetime.strptime('2022-10-31', '%Y-%m-%d')
        endTime = datetime.now().date().strftime("%Y-%m-%d")
        startTime = (datetime.now() - timedelta(days=0)).date().strftime("%Y-%m-%d")
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

    def add_routes(self, app):

        # @app.route('/fitbit_auth', methods=['GET','POST'])
        # def fitbit_auth():
        #     state = request.args.get('state')
        #     code = request.args.get('code')
        #     error = request.args.get('error')
        #     endpoint = request.args.get('endpoint')
        #     print('fitbit_auth', state, code, error)
        #     """
        #     Receive a Fitbit response containing a verification code. Use the code
        #     to fetch the access_token.
        #     """
        #     error = None
        #     if code:
        #         try:
        #             self.fitbit.client.fetch_access_token(code)
        #             # self.ACCESS_TOKEN=code
        #             # self.REFRESH_TOKEN=state
        #             # print('setting access token', self.ACCESS_TOKEN)
        #         except MissingTokenError:
        #             error = self._fmt_failure(
        #                 'Missing access token parameter.</br>Please check that '
        #                 'you are using the correct client_secret')
        #         except MismatchingStateError:
        #             error = self._fmt_failure('CSRF Warning! Mismatching state')
        #     else:
        #         error = self._fmt_failure('Unknown error while authenticating')
        #     # Use a thread to shutdown cherrypy so we can return HTML first
        #     return error if error else self.success_html
        
        # from flask import Blueprint

        # heart_rate_bp = Blueprint('heart_rate_bp', __name__)

        # @heart_rate_bp.route('/heartRate')
        # def heartRate():
        #     # your route implementation here


        @app.route('/heartRate', methods=['GET'])
        def heartRate():
            self.authorize()
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
        #         values.setdefault('random', str(random.randint(0, 999999)))

        # @app.url_value_preprocessor
        # def check_random_number(endpoint, values):
        #     if endpoint == 'heartRate':
        #         if 'random' not in values:
        #             return 'Invalid request', 400
        
        # app.register_blueprint(heart_rate_bp, lazy_load=True)

        return app