import json
import requests
import pandas as pd 
from flask import redirect, url_for, request
from flask_login import current_user
from urllib.parse import quote

from src import getSecret, isRunningInCloud, CLOUD_URL, FLASK_PORT

class Spotify_API:
    FLASK_AUTHORIZATION = '/authorize_spotify'
    def __init__(self, db, serverLess=False):

        #  Client Keys
        self.CLIENT_ID = getSecret('SPOTIFY_CLIENT_ID')
        self.CLIENT_SECRET = getSecret('SPOTIFY_CLIENT_SECRET')

        # Spotify URLS
        SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
        self.SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
        SPOTIFY_API_BASE_URL = "https://api.spotify.com"
        API_VERSION = "v1"
        self.SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

        # Server-side Parameters
        if isRunningInCloud():
            CLIENT_SIDE_URL = CLOUD_URL
            self.REDIRECT_URI = "{}/authorize_spotify".format(CLIENT_SIDE_URL)
        else:
            CLIENT_SIDE_URL = "http://127.0.0.1"
            PORT = 8080
            self.REDIRECT_URI = "{}:{}/authorize_spotify".format(CLIENT_SIDE_URL, PORT)
        
        SCOPE = "user-read-recently-played, user-top-read, user-read-currently-playing, playlist-modify-public playlist-modify-private"
        STATE = ""

        # self.client_id = os.environ.get('SPOTIFY_CLIENT_ID')
        # self.client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')

        auth_query_parameters = {
            "response_type": "code",
            "redirect_uri": self.REDIRECT_URI,
            "scope": SCOPE,
            # "state": STATE,
            # "show_dialog": SHOW_DIALOG_str,
            "client_id": self.CLIENT_ID
        }

        SHOW_DIALOG_bool = True
        SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()

        # building the spotify authenication url
        url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in auth_query_parameters.items()])
        self.auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)

        self.db = db
    
    def search(self):
        d = []

        total = 1 # temporary variable
        offset = 0

        while offset < total:
            results = self.sp.search(q="artist:guns n' roses",  type='track', offset=offset, limit=50)
            total = results['tracks']['total']
            offset += 50 # increase the offset
            for idx, track in enumerate(results['tracks']['items']):
                d.append (
                    {
                        'Track' : track['name'],
                        'Album' : track['album']['name'],
                        'Artist' : track['artists'][0]['name'],
                        'Release Date' : track['album']['release_date'],            
                        'Track Number' : track['track_number'],
                        'Popularity' : track['popularity'],
                        'Track Number' : track['track_number'],
                        'Explicit' : track['explicit'],
                        'Duration' : track['duration_ms'],
                        'Audio Preview URL' : track['preview_url'],
                        'Album URL' : track['album']['external_urls']['spotify']
                    }
                )
        pd.DataFrame(d)

    def authorize(self):
        """
        
        """
        if not current_user.spotify_authorized:
            return redirect(self.auth_url)
    
    def buildAuthHeader(self):
        return {"Authorization": "Bearer {}".format(current_user.spotify_token)}
    
    def requestHandler(self, endpoint, params={}):
        response = requests.get(endpoint, headers=self.buildAuthHeader(), params=params)
        data = json.loads(response.text)
        if 'error' in data and data['error']['status'] == 401:
            if 'message' in data['error'] and data['error']['message'] == "The access token expired":   
                self.refreshToken()
                return self.requestHandler(endpoint, params=params)
        else:
            return data

    def user_data(self):
        user_profile_api_endpoint = "{}/me".format(self.SPOTIFY_API_URL)
        profile_data = self.requestHandler(user_profile_api_endpoint)

        playlist_api_endpoint = "{}/playlists".format(profile_data["href"])
        playlist_data = self.requestHandler(playlist_api_endpoint)
        display_arr = [profile_data] + playlist_data["items"]
        return display_arr
    
    def recentlyPlayedData(self, num_entries=50):
        recently_played_api_endpoint = "{}/me/player/recently-played".format(self.SPOTIFY_API_URL)
        recently_played_data = self.requestHandler(recently_played_api_endpoint, params={'limit': num_entries})
        df_played = pd.DataFrame(recently_played_data['items'])
        df_played['name'] = df_played['track'].apply(lambda x: x['name'])
        df_played['artist'] = df_played['track'].apply(lambda x: x['artists'][0]['name'])
        df_played['song_id'] = df_played['track'].apply(lambda x: x['id']) 
        df_played['duration_ms'] = df_played['track'].apply(lambda x: x['duration_ms'])
        df_played['songImage'] = df_played['track'].apply(lambda x: x['album']['images'][0]['url'])
        df_played = df_played.drop(columns=['track', 'context'])
        df_played['played_at'] = pd.to_datetime(df_played['played_at'])
        # HACKY convert to EST
        df_played['played_at'] = df_played['played_at'] - pd.Timedelta(hours=4)

        return df_played

    def getAudioFeatures(self, df_played):
        audio_features_api_endpoint = "{}/audio-features".format(self.SPOTIFY_API_URL)
        audio_features = self.requestHandler(audio_features_api_endpoint, params={'ids': ','.join(df_played['song_id'].to_list())})
        df_audio_features = pd.DataFrame(audio_features)
        df_audio_features = pd.concat([df_audio_features['audio_features'].apply(pd.Series)], axis=1)
        df_played = pd.concat([df_played, df_audio_features], axis=1)
        return df_played
    
    def getRecentlyPlayedWithFeatures(self, num_entries=50):
        df_played = self.recentlyPlayedData(num_entries)
        df_played = self.getAudioFeatures(df_played)
        return df_played
    
    def refreshAccessToken(self):
        if current_user.spotify_refresh_token is None:
            raise ValueError("Refresh token is not set.")
        post_data = {
            "grant_type": "refresh_token",
            "refresh_token": current_user.spotify_refresh_token,
            "client_id": self.CLIENT_ID,
            "client_secret": self.CLIENT_SECRET
        }
        post_request = requests.post(self.SPOTIFY_TOKEN_URL, data=post_data)
        response_data = json.loads(post_request.text)

        self.access_token = response_data["access_token"]
        self.token_type = response_data["token_type"]
        self.expires_in = response_data["expires_in"]
        
        current_user.spotify_authorized = True
        current_user.spotify_token = response_data["access_token"]
        self.db.session.commit()

    def add_routes(self, app, db, spotify_and_fitbit_authorized_required):

        @app.route("/authorize_spotify")
        def authorize_spotify():
            auth_token = request.args['code']
            code_payload = {
                "grant_type": "authorization_code",
                "code": str(auth_token),
                "redirect_uri": self.REDIRECT_URI,
                'client_id': self.CLIENT_ID,
                'client_secret': self.CLIENT_SECRET,
            }
            post_request = requests.post(self.SPOTIFY_TOKEN_URL, data=code_payload)

            response_data = json.loads(post_request.text)
            access_token = response_data["access_token"]
            refresh_token = response_data["refresh_token"]
            token_type = response_data["token_type"]
            expires_in = response_data["expires_in"]    
            
            current_user.spotify_token = response_data["access_token"]
            current_user.spotify_refresh_token = response_data["refresh_token"]
            current_user.spotify_authorized = True
            db.session.commit()
            
            return  redirect(url_for('home'))
        
        @app.route('/user_authorize_spotify', methods=['GET'])
        def user_authorize_spotify():
            page = self.authorize()
            if page:
                return page
            return redirect(url_for('home'))

        @app.route('/recentlyPlayed', methods=['GET'])
        @spotify_and_fitbit_authorized_required
        def recentlyPlayed():
            return self.recentlyPlayedData().to_dict(orient='records')
        
        @app.route('/recentlyPlayedWithFeatures', methods=['GET'])
        @spotify_and_fitbit_authorized_required
        def recentlyPlayedWithFeatures():
            return self.getRecentlyPlayedWithFeatures().to_dict(orient='records')
            
        return app