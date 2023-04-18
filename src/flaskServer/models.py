from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(120), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(30))
    fitbit_authorized = db.Column(db.Boolean, default=False)
    fitbit_access_token = db.Column(db.String(300))
    fitbit_refresh_token = db.Column(db.String(200))
    spotify_authorized = db.Column(db.Boolean, default=False)
    spotify_token = db.Column(db.String(300))
    spotify_refresh_token = db.Column(db.String(200))

    def __init__(self, username=None, email=None):
        self.username = username
        self.email = email
    def set_password(self, password):
        self.password = password
    def check_password(self, password):
        return self.password == password
    def is_active(self):
        return True

class Song(db.Model):
    __tablename__ = 'songs'
    # general song info
    song_id = db.Column(db.String(50), primary_key=True)
    artist = db.Column(db.String(120))
    name = db.Column(db.String(120))
    duration_ms = db.Column(db.Integer)
    song_image = db.Column(db.String(120))
    # audio features
    acousticness = db.Column(db.Float)
    danceability = db.Column(db.Float)
    energy = db.Column(db.Float)
    instrumentalness = db.Column(db.Float)
    key = db.Column(db.Integer)
    liveness = db.Column(db.Float)
    loudness = db.Column(db.Float)
    mode = db.Column(db.Integer)
    speechiness = db.Column(db.Float)
    tempo = db.Column(db.Float)
    time_signature = db.Column(db.Integer)
    valence = db.Column(db.Float)

    def __init__(self, data):
        self.song_image = data['song_image']
        self.song_id = data['song_id']
        self.duration_ms = data['duration_ms']
        self.artist = data['artist']
        self.name = data['name']

        self.acousticness = data['acousticness']
        self.danceability = data['danceability']
        self.energy = data['energy']
        self.instrumentalness = data['instrumentalness']
        self.key = data['key']
        self.liveness = data['liveness']
        self.loudness = data['loudness']
        self.mode = data['mode']
        self.speechiness = data['speechiness']
        self.tempo = data['tempo']
        self.time_signature = data['time_signature']
        self.valence = data['valence']

class MusicHistory(db.Model):
    __tablename__ = 'music_history'
    song_id = db.Column(db.String(50), primary_key=True)
    played_at = db.Column(db.DateTime, primary_key=True)
    user_id = db.Column(db.Integer, primary_key=True)

    def __init__(self, song_id, played_at, user_id):
        self.song_id = song_id
        self.played_at = played_at
        self.user_id = user_id

class HeartRate(db.Model):
    __tablename__ = 'heart_rate'
    user_id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime, primary_key=True)
    bpm = db.Column(db.Integer, nullable=False)

    def __init__(self, user_id, bpm, datetime):
        self.user_id = user_id
        self.bpm = bpm
        self.datetime = datetime

class Modes(db.Model):
    __tablename__ = 'modes'
    mode_id = db.Column(db.Integer, primary_key=True)
    mode_name = db.Column(db.String(50), nullable=False)

    def __init__(self, mode_id, mode_name):
        self.mode_id = mode_id
        self.mode_name = mode_name

class RunningModes(db.Model):
    __tablename__ = 'running_modes'
    user_id = db.Column(db.Integer, primary_key=True)
    # datetime = db.Column(db.DateTime, primary_key=True)
    mode_id = db.Column(db.Integer, nullable=False)

    def __init__(self, user_id, mode_id):
        self.user_id = user_id
        self.mode_id = mode_id    

class PlaylistsForMode(db.Model):
    __tablename__ = 'playlists_for_mode'
    mode_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.String(50), primary_key=True)

    def __init__(self, mode_id, user_id, playlist_id):
        self.mode_id = mode_id
        self.user_id = user_id
        self.playlist_id = playlist_id

class Playlist(db.Model):
    __tablename__ = 'playlists'
    user_id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.String(50), primary_key=True)
    playlist_name = db.Column(db.String(50), nullable=False)
    playlist_image_url = db.Column(db.String(200), nullable=False)

    def __init__(self, user_id, playlist_id, playlist_name, playlist_image_url):
        self.user_id = user_id
        self.playlist_id = playlist_id
        self.playlist_name = playlist_name
        self.playlist_image_url = playlist_image_url