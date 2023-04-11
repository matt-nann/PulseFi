import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import pandas as pd

import sys
import traceback
import datetime
from datetime import datetime, timedelta

import pandas as pd 
from fitbit.api import Fitbit
from flask import redirect, url_for, request
from oauthlib.oauth2.rfc6749.errors import MismatchingStateError, MissingTokenError

from __init__ import getSecret, isRunningInCloud, CLOUD_URL, FLASK_PORT

import json
from flask import Flask, request, redirect, g, render_template
import requests
from urllib.parse import quote

# Authentication Steps, paramaters, and responses are defined at https://developer.spotify.com/web-api/authorization-guide/
# Visit this url to see all the steps, parameters, and expected response.


# # Process each track
# for item in results['items']:
#     track = item['track']
#     track_name = track['name']
#     artist_name = track['artists'][0]['name']
#     track_id = track['id']
    
#     # Get audio features for the track
#     audio_features = sp.audio_features([track_id])
#     bpm = audio_features[0]['tempo']
    
#     # Print characteristics and BPM for the track
#     print(f"{track_name} by {artist_name} (BPM: {bpm})")


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

        self.unauthorized = True
        self.failedAuth = False
    
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
        if self.failedAuth:
            return 'Failed to authorize Fitbit'
        if self.unauthorized:
            return redirect(self.auth_url)
        
    def user_data(self):
        user_profile_api_endpoint = "{}/me".format(self.SPOTIFY_API_URL)
        profile_response = requests.get(user_profile_api_endpoint, headers=self.authorization_header)
        profile_data = json.loads(profile_response.text)
        # return profile_data

        playlist_api_endpoint = "{}/playlists".format(profile_data["href"])
        playlists_response = requests.get(playlist_api_endpoint, headers=self.authorization_header)
        playlist_data = json.loads(playlists_response.text)
        display_arr = [profile_data] + playlist_data["items"]
        return display_arr
    
    def recentlyPlayed(self, num_entries=50):
        recently_played_api_endpoint = "{}/me/player/recently-played".format(self.SPOTIFY_API_URL)
        recently_played_response = requests.get(recently_played_api_endpoint, headers=self.authorization_header, params={'limit': num_entries})
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

    def add_routes(self, app):

        @app.route("/authorize_spotify")
        def callback():
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
            self.access_token = response_data["access_token"]
            refresh_token = response_data["refresh_token"]
            token_type = response_data["token_type"]
            expires_in = response_data["expires_in"]    
            self.authorization_header = {"Authorization": "Bearer {}".format(self.access_token)}
            self.unauthorized = False
            
            return redirect(url_for('recentlyPlayed'))

        @app.route('/recentlyPlayed', methods=['GET'])
        def recentlyPlayed():
            page = self.authorize()
            if page:
                return page
            return self.recentlyPlayed().to_html()
            
        return app