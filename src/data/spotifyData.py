import json
import requests
import pandas as pd 
from flask import redirect, url_for, request
from flask_login import current_user
from urllib.parse import quote

from src import getSecret, isRunningInCloud, CLOUD_URL, FLASK_PORT

class Spotify_API:
    FLASK_AUTHORIZATION = '/authorize_spotify'
    def __init__(self, serverLess=False):

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

    def user_data(self):
        user_profile_api_endpoint = "{}/me".format(self.SPOTIFY_API_URL)
        profile_response = requests.get(user_profile_api_endpoint, headers=self.buildAuthHeader())
        profile_data = json.loads(profile_response.text)
        # return profile_data

        playlist_api_endpoint = "{}/playlists".format(profile_data["href"])
        playlists_response = requests.get(playlist_api_endpoint, headers=self.buildAuthHeader())
        playlist_data = json.loads(playlists_response.text)
        display_arr = [profile_data] + playlist_data["items"]
        return display_arr
    
    def recentlyPlayed(self, num_entries=50):
        recently_played_api_endpoint = "{}/me/player/recently-played".format(self.SPOTIFY_API_URL)
        recently_played_response = requests.get(recently_played_api_endpoint, headers=self.buildAuthHeader(), params={'limit': num_entries})
        recently_played_data = json.loads(recently_played_response.text)
        df_played = pd.DataFrame(recently_played_data['items'])
        df_played['name'] = df_played['track'].apply(lambda x: x['name'])
        df_played['artist'] = df_played['track'].apply(lambda x: x['artists'][0]['name'])
        df_played['song_id'] = df_played['track'].apply(lambda x: x['id']) 
        df_played['duration_ms'] = df_played['track'].apply(lambda x: x['duration_ms'])
        df_played['songImage'] = df_played['track'].apply(lambda x: x['album']['images'][0]['url'])
        df_played = df_played.drop(columns=['track', 'context'])
        return df_played

    def getSongInfo(self, df):
        df_played = df_played.drop(columns=['track', 'context'])
        for row in df_played.iterrows():
            track = row['track']
            track_name = row['name']
            artist_name = row['artists'][0]['name']
            track_id = row['id']
            # Get audio features for the track
            audio_features = self.sp.audio_features([track_id])
            bpm = audio_features[0]['tempo']
            # Print characteristics and BPM for the track
            print(f"{track_name} by {artist_name} (BPM: {bpm})")

        return df_played

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
            return self.recentlyPlayed().to_dict(orient='records')
            
        return app