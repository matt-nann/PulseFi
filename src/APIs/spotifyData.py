import json
import requests
import pandas as pd 
from datetime import datetime, timezone
from flask import redirect, url_for, request, make_response, jsonify
from flask_login import current_user
from urllib.parse import quote
import random

from src import getSecret, isRunningInCloud, CLOUD_URL, ModesTypes_Values
from src.sql import get_dataframe_from_query
from src.flaskServer.models import PlaylistsForMode, Modes, Playlist, MusicHistory, Song   

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
        SCOPE += " user-read-playback-state"
        SCOPE += " user-modify-playback-state" # have the API change the currently playing music
        STATE = ""

        # self.client_id = os.environ.get('SPOTIFY_CLIENT_ID')
        # self.client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')heartRateData allDates:

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

        # response_data["token_type"] response_data["expires_in"]
        
        current_user.spotify_authorized = True
        current_user.spotify_token = response_data["access_token"]
        print("Refreshed access token")
        self.db.session.commit()
    
    def getRequest(self, endpoint, params={}):
        response = requests.get(endpoint, headers=self.buildAuthHeader(), params=params)
        data = json.loads(response.text)
        if 'error' in data and data['error']['status'] == 401:
            expiredAccessToken = 'message' in data['error'] and data['error']['message'] == "The access token expired"
            invalidAccessToken = 'message' in data['error'] and data['error']['message'] == "Invalid access token"
            if expiredAccessToken or invalidAccessToken:
                self.refreshAccessToken()
                return self.getRequest(endpoint, params=params)
            print("getRequest: ", data)
        else:
            return data
        
    def postRequest(self, endpoint, data={}):
        response = requests.put(endpoint, data=json.dumps(data), headers=self.buildAuthHeader())
        if response.status_code == 204:
            return {}
        else:
            return response.json()

    def user_data(self):
        user_profile_api_endpoint = "{}/me".format(self.SPOTIFY_API_URL)
        profile_data = self.getRequest(user_profile_api_endpoint)

        playlist_api_endpoint = "{}/playlists".format(profile_data["href"])
        playlist_data = self.getRequest(playlist_api_endpoint)
        display_arr = [profile_data] + playlist_data["items"]
        return display_arr
    
    def userPlaylists(self):
        user_profile_api_endpoint = "{}/me".format(self.SPOTIFY_API_URL)
        profile_data = self.getRequest(user_profile_api_endpoint)
        playlist_api_endpoint = "{}/playlists".format(profile_data["href"])
        _playlist_data = self.getRequest(playlist_api_endpoint)
        _playlist_data["items"]
        playlist_Data = []
        for playlist in _playlist_data["items"]:
            playlist_Data.append({
                "name": playlist["name"],
                "id": playlist["id"],
                "image_url": playlist["images"][0]["url"] if len(playlist["images"]) > 0 else "",
                "selected": []
            })
        return playlist_Data
    
    def recentlyPlayedData(self, num_entries=50):
        recently_played_api_endpoint = "{}/me/player/recently-played".format(self.SPOTIFY_API_URL)
        recently_played_data = self.getRequest(recently_played_api_endpoint, params={'limit': num_entries})
        df_played = pd.DataFrame(recently_played_data['items'])
        df_played['name'] = df_played['track'].apply(lambda x: x['name'])
        df_played['artist'] = df_played['track'].apply(lambda x: x['artists'][0]['name'])
        df_played['song_id'] = df_played['track'].apply(lambda x: x['id']) 
        df_played['duration_ms'] = df_played['track'].apply(lambda x: x['duration_ms'])
        df_played['song_image'] = df_played['track'].apply(lambda x: x['album']['images'][0]['url'])
        df_played = df_played.drop(columns=['track', 'context'])
        df_played['played_at'] = pd.to_datetime(df_played['played_at'])
        # HACKY convert to EST
        df_played['played_at'] = df_played['played_at'] - pd.Timedelta(hours=4)
        return df_played

    def getAudioFeatures(self, df_played):
        audio_features_api_endpoint = "{}/audio-features".format(self.SPOTIFY_API_URL)
        audio_features = self.getRequest(audio_features_api_endpoint, params={'ids': ','.join(df_played['song_id'].to_list())})
        df_audio_features = pd.DataFrame(audio_features)
        valid_songs = df_audio_features['audio_features'].apply(lambda x: x is not None)
        df_audio_features = df_audio_features[valid_songs]
        valid_song_ids = df_audio_features['audio_features'].apply(lambda x: x['id']).to_list()
        all_song_ids = df_played['song_id'].to_list()
        df_audio_features = pd.concat([df_audio_features['audio_features'].apply(pd.Series)], axis=1)
        df_played = df_played.drop(columns=['duration_ms'])
        df_played = pd.concat([df_played, df_audio_features], axis=1)
        df_played = df_played.drop(columns=['id', 'uri', 'track_href', 'analysis_url','type'])
        df_played['user_id'] = current_user.id
        # TODO if a song doesn't have audio-features the current solution is to just drop it from the music history
        df_played = df_played[df_played['song_id'].isin(valid_song_ids)]
        # df_played = df_played.where(pd.notnull(df_played), None)
        return df_played
    
    def get_music_history_df(self, current_user):
        df = get_dataframe_from_query("SELECT music_history.*, songs.* FROM music_history JOIN songs ON music_history.song_id = songs.song_id WHERE user_id = {}".format(current_user.id))
        # there are two song_id columns and even with df = df.drop_duplicates(subset=['song_id'], keep='first'), the remaining song_id column would be a pandas series
        temp = df['song_id'].iloc[:,0]
        df = df.drop(columns=['song_id'])
        df.insert(0, 'song_id', temp)
        df.set_index('played_at', inplace=True)
        df.index = df.index.tz_localize(None)
        return df

    def currentlyPlaying(self):
        now_playing_data = self.getRequest("{}/me/player/currently-playing".format(self.SPOTIFY_API_URL))
        timestamp = now_playing_data['timestamp']
        progress_ms = now_playing_data['progress_ms']
        album = now_playing_data['item']['album']['name']
        duration_ms = now_playing_data['item']['duration_ms']
        song = now_playing_data['item']['name']
        artist = now_playing_data['item']['artists'][0]['name']
        artist_id = now_playing_data['item']['artists'][0]['id']
        is_playing = now_playing_data['is_playing']
        song_id = now_playing_data['item']['id']

        class CurrentSong:
            def __init__(self, song, song_id, artist, artist_id, timestamp, progress_ms, album, duration_ms, is_playing):
                self.song = song
                self.song_id = song_id
                self.artist = artist
                self.artist_id = artist_id
                self.timestamp = timestamp
                self.progress_ms = progress_ms
                self.album = album
                self.duration_ms = duration_ms
                self.is_playing = is_playing
            def __str__(self):
                return f"CurrentSong({self.song}, {self.song_id}, {self.artist}, {self.artist_id}, {self.timestamp}, {self.progress_ms}, {self.album}, {self.duration_ms}, {self.is_playing})"
                
        current_song = CurrentSong(song, song_id, artist, artist_id, timestamp, progress_ms, album, duration_ms, is_playing)
        return current_song
    
    def getActiveDeviceId(self):
        devices = self.getRequest("{}/me/player/devices".format(self.SPOTIFY_API_URL)) 
        for device in devices['devices']:
            if device['is_active']:
                return device['id']
        return None

    def playSong(self, song_id, device_id=None):
        if device_id is None:
            device_id = self.getActiveDeviceId()
            if device_id is None:
                return make_response(jsonify({'error': 'No active device found'}), 405)
        response = self.postRequest("{}/me/player/play".format(self.SPOTIFY_API_URL), data={'uris': ['spotify:track:' + song_id], 'device_id': device_id})
        if 'error' in response and response['error']['status'] == 404:
            if 'message' in response['error'] and response['error']['message'] == 'Player command failed: No active device found':  
                return make_response(jsonify({'error': 'No active device found'}), 405)
        return 'Song played successfully'
        
    def playRandomSong(self):
        df = get_dataframe_from_query("SELECT * from songs;")
        next_song_id = df['song_id'].sample().iloc[0]
        return self.playSong(next_song_id)
    
    def getRecentlyPlayedWithFeatures(self, num_entries=50):
        # Get stored data from database
        stored_data_df = self.get_music_history_df(current_user)

        # Get new data from API
        new_data_df = self.recentlyPlayedData(num_entries)
        new_song_ids = new_data_df['song_id'].unique()

        new_data_df = self.getAudioFeatures(new_data_df)
        new_data_df.set_index('played_at', inplace=True)
        new_data_df.index = new_data_df.index.tz_localize(None)

        # Check which song IDs are not in the Song table and insert them
        existing_songs = Song.query.filter(Song.song_id.in_(new_song_ids)).all()
        existing_song_ids = [song.song_id for song in existing_songs]
        new_song_ids = list(set(new_song_ids) - set(existing_song_ids))
        new_songs = []
        newlyAddedSongsIds = []
        if new_song_ids:
            for index, row in new_data_df.iterrows():
                if row['song_id'] in new_song_ids and row['song_id'] not in newlyAddedSongsIds:
                    new_song = Song(row)
                    newlyAddedSongsIds.append(new_song.song_id)
                    new_songs.append(new_song)
            self.db.session.add_all(new_songs)

        # Find the most recently played song, and insert all newly played songs after it
        latest_played_at = self.db.session.query(self.db.func.max(MusicHistory.played_at)).filter_by(user_id=current_user.id).scalar()
        if latest_played_at:
            df_new_songs = new_data_df[new_data_df.index > latest_played_at]
        else:
            df_new_songs = new_data_df.copy()

        new_History = []
        for index, row in df_new_songs.iterrows():
            song_id = row['song_id']
            played_at = index
            playedSong = MusicHistory(song_id=song_id, played_at=played_at, user_id=current_user.id)
            new_History.append(playedSong)
        self.db.session.add_all(new_History)
        self.db.session.commit()

        df_combined = pd.concat([stored_data_df, df_new_songs], axis=0)
        df_combined = df_combined.sort_values(by=['played_at'], ascending=False)
        df_combined['played_at'] = df_combined.index
        df_combined.reset_index(drop=True, inplace=True)
        return df_combined
    
    def getPlaylistSongIDs(self, playlist_id):
        playlist_api_endpoint = "{}/playlists/{}/tracks".format(self.SPOTIFY_API_URL, playlist_id)
        playlist_data = self.getRequest(playlist_api_endpoint)
        song_ids = [item['track']['id'] for item in playlist_data['items']]
        return song_ids

    def add_routes(self, app, db, spotify_and_fitbit_authorized_required, login_required):

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
            token_type = response_data["token_type"]
            expires_in = response_data["expires_in"]    
            
            current_user.spotify_token = response_data["access_token"]
            current_user.spotify_refresh_token = response_data["refresh_token"]
            current_user.spotify_authorized = True
            db.session.commit()
            
            return  redirect(url_for('home'))
        
        @app.route('/user_authorize_spotify', methods=['GET'])
        @login_required()
        def user_authorize_spotify():
            page = self.authorize()
            if page:
                return page
            return redirect(url_for('home'))
        
        @app.route('/startMode', methods=['POST'])
        @spotify_and_fitbit_authorized_required
        def startMode():
            mode_id = request.json.get('mode_id', None)
            if mode_id is None or int(mode_id) not in ModesTypes_Values:
                return make_response(jsonify({'error': 'No mode_id provided', 'text': 'No mode_id provided'}), 400)
            usedPlaylists = PlaylistsForMode.query.filter_by(mode_id=mode_id, user_id=current_user.id).all()
            if usedPlaylists:
                song_ids = []
                for playlist in usedPlaylists:
                    _ = self.getPlaylistSongIDs(playlist.playlist_id)
                    if _:
                        song_ids.extend(_)
                if song_ids:
                    song_id = random.choice(song_ids)
                    result = self.playSong(song_id)
                    print(result)
                    return result
                else:
                    return make_response(jsonify({'error': 'No songs found in playlists for this mode'}), 400)
            else:
                return make_response(jsonify({'error': 'No playlists found for this mode'}), 400)

        @app.route('/recentlyPlayed', methods=['GET'])
        @spotify_and_fitbit_authorized_required
        def recentlyPlayed():
            # return self.get_music_history_df(current_user).to_html()
            return self.getRecentlyPlayedWithFeatures().to_dict(orient='records')
        
        @app.route('/recentlyPlayedWithFeatures', methods=['GET'])
        @spotify_and_fitbit_authorized_required
        def recentlyPlayedWithFeatures():
            return self.getRecentlyPlayedWithFeatures().to_dict(orient='records')
        
        @app.route('/playRandomSong', methods=['POST'])
        @spotify_and_fitbit_authorized_required
        def playRandomSong():
            return self.playRandomSong()
        
        @app.route('/userData', methods=['GET'])
        @spotify_and_fitbit_authorized_required
        def userData():
            return self.user_data()
            
        @app.route('/userPlaylists', methods=['GET'])
        @spotify_and_fitbit_authorized_required
        def userPlaylists():
            return self.userPlaylists()
        
        @app.route('/getActiveDeviceId', methods=['GET'])
        @spotify_and_fitbit_authorized_required
        def getActiveDeviceId():
            return self.getActiveDeviceId()

        return app