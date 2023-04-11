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
        self.client_id = os.environ.get('SPOTIFY_CLIENT_ID')
        self.client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')

        # Set up authentication
        scope = "user-read-recently-played, user-top-read, user-read-currently-playing" #, user-read-playback-state, user-modify-playback-state, user-read-playback-position, user-read-private, user-read-email, user-library-read, user-library-modify, playlist-read-private, playlist-read-collaborative, playlist-modify-public, playlist-modify-private, streaming, app-remote-control, user-read-playback-state, user-modify-playback-state, user-read-currently-playing, user-read-recently-played"
        # if serverLess:
        #     redirect_uri = "http://localhost:8888/callback"
        # elif isRunningInCloud():
        #     redirect_uri = CLOUD_URL + self.FLASK_AUTHORIZATION
        # else:
        #     redirect_uri = 'http://127.0.0.1:' + str(FLASK_PORT) + self.FLASK_AUTHORIZATION
        redirect_uri = "http://localhost:8888/callback"

        self.auth_manager = SpotifyOAuth(scope=scope, client_id=self.client_id, client_secret=self.client_secret, redirect_uri=redirect_uri)
        self.sp = spotipy.Spotify(auth_manager=self.auth_manager)

        self.unauthorized = True
        self.failedAuth = False

    def recentlyPlayed(self):
        results = self.sp.current_user_recently_played(limit=50)
        df_played = pd.DataFrame(results['items'])
        df_played['name'] = df_played['track'].apply(lambda x: x['name'])
        df_played['artist'] = df_played['track'].apply(lambda x: x['artists'][0]['name'])
        df_played['song_id'] = df_played['track'].apply(lambda x: x['id']) 
        df_played['duration_ms'] = df_played['track'].apply(lambda x: x['duration_ms'])
        df_played['songImage'] = df_played['track'].apply(lambda x: x['album']['images'][0]['url'])

        # drop track
        df_played = df_played.drop(columns=['track', 'context'])

        # # Process each track
        # for item in results['items']:
        #     track = item['track']
        #     track_name = track['name']
        #     artist_name = track['artists'][0]['name']
        #     track_id = track['id']
            
        #     # Get audio features for the track
        #     audio_features = self.sp.audio_features([track_id])
        #     bpm = audio_features[0]['tempo']
            
        #     # Print characteristics and BPM for the track
        #     print(f"{track_name} by {artist_name} (BPM: {bpm})")

        return df_played
    
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
    
    def add_routes(self, app):

        # @app.route(self.FLASK_AUTHORIZATION, methods=['GET','POST'])
        # def authorize_spotify():
        #     print(request.args)
        #     code = request.args.get('code')

        #     self.unauthorized = False
        #     return redirect(url_for('recentlyPlayed'))

        @app.route('/recentlyPlayed', methods=['GET'])
        def recentlyPlayed():
            return self.recentlyPlayed().to_html()
            # if self.unauthorized:
            #     return redirect(url_for('authorize_spotify'))
            # else:
            #     return 

        return app