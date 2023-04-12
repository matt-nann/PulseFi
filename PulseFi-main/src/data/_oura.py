from oura.v2 import OuraClientV2, OuraClientDataFrameV2
import requests 
from datetime import datetime, timedelta
import pandas as pd

from src import getSecret

class OuraData(): 

    def __init__(self):
        '''
        TODO
        '''

        self.oura_headers = { 
            'Authorization': 'Bearer ' + getSecret('OURA_KEY') 
        }

    def ouraParams(self):
        params={ 
            'start_date': '2022-01-01', 
            'end_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
        }
        return params

    def apiFunctions(self):

        ouraClient = OuraClientV2(personal_access_token=getSecret('OURA_KEY'))
        ouraClient_df = OuraClientDataFrameV2(personal_access_token=getSecret('OURA_KEY'))

        # functions available in the API
        daily_activity = ouraClient_df.daily_activity()
        heart_rate_sleepDaily = ouraClient_df.heart_rate_df()
        heartrate = ouraClient_df.heartrate()
        personal_info = ouraClient_df.personal_info()
        personal_info_df = ouraClient_df.personal_info_df()
        session = ouraClient_df.session()
        sessions_df = ouraClient_df.sessions_df()
        # functions that haven't been implemented in the api
        # sleep_df = ouraClient_df.sleep_df()
        # tags = ouraClient_df.tags()
        # tags_df = ouraClient_df.tags_df()
        # workouts = ouraClient_df.workouts()
        # workouts_df = ouraClient_df.workouts_df()
        # readiness_df = ouraClient_df.readiness_df()

        t1 = ouraClient.daily_activity()
        t2 = ouraClient.heartrate()
        t3 = ouraClient.personal_info()
        t4 = ouraClient.session()
        t5 = ouraClient.tags()
        t6 = ouraClient.workouts()

    def dailySleep(self):
        url = 'https://api.ouraring.com/v2/usercollection/daily_sleep' 
        response = requests.request('GET', url, headers=self.oura_headers, params=self.ouraParams()) 
        sleepDaily = pd.read_json(response.text)
        sleepDaily = pd.concat([sleepDaily.drop(['data'], axis=1), sleepDaily['data'].apply(pd.Series)], axis=1)
        sleepDaily = pd.concat([sleepDaily.drop(['contributors'], axis=1), sleepDaily['contributors'].apply(pd.Series)], axis=1)
        sleepDaily.drop(['next_token','day'], inplace=True, axis=1)
        sleepDaily['day'] = pd.to_datetime(sleepDaily['timestamp']).dt.tz_convert('UTC').dt.date
        # sleepDaily.drop(['next_token','day','timestamp'], inplace=True, axis=1)
        sleepDaily.rename(columns={'score':'sleepScore'}, inplace=True)
        return sleepDaily
    def detailedSleep(self):
        url = 'https://api.ouraring.com/v2/usercollection/sleep' 
        response = requests.request('GET', url, headers=self.oura_headers, params=self.ouraParams()) 
        df = pd.read_json(response.text)
        df = pd.concat([df.drop(['data'], axis=1), df['data'].apply(pd.Series)], axis=1)
        df.drop(['next_token'],inplace=True,axis=1)
        df = pd.concat([df.drop(['readiness'], axis=1), df['readiness'].apply(pd.Series, dtype='object')], axis=1)
        df.rename(columns={'score': 'readiness_score'}, inplace=True)
        df['day'] = pd.to_datetime(df['day']).dt.date
        return df
    def nightlySleep(self):
        sleepDaily = self.dailySleep()
        sleepData = self.detailedSleep()
        sleepData = sleepData.loc[sleepData['type'] == 'long_sleep']
        sleepData = sleepData.merge(sleepDaily, how='left', on='day')
        return sleepData

    def saveData(self):
        df_download = pd.read_csv('oura_2022-01-17_2022-12-21_trends.csv')