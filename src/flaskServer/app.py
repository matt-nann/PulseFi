import os
from flask import Flask, render_template, request, flash, redirect, url_for, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
import logging
from functools import wraps
from logging import Formatter, FileHandler
import json
import ast
from flask_wtf.csrf import CSRFProtect
from markupsafe import Markup

from src import getSecret, isRunningInCloud, baseUrl, ModesTypes 
from src.APIs.fitbitData import Fitbit_API
from src.APIs.spotifyData import Spotify_API
from src.APIs.ouraData import Oura_API
from src.dashboard import add_dash_routes
from src.flaskServer.config import Config
from src.flaskServer.forms import *
from src.flaskServer.models import User, db, PlaylistsForMode, Modes, RunningModes, Playlist

def json_script(obj, var_name):
    json_str = json.dumps(obj)
    script = f'<script>var {var_name} = {json_str};</script>'
    return Markup(script)

def create_app():

    app = Flask(__name__)
    csrf = CSRFProtect(app)

    # Add the filter to the Jinja2 environment
    app.jinja_env.filters['json_script'] = json_script

    app.config.from_object(Config)
    
    login_manager = LoginManager()
    login_manager.init_app(app)

    db.init_app(app)
    migrate = Migrate(app, db)
    with app.app_context():
        db.create_all()
        # engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        # print('engine created', engine)
        # db.session.configure(bind=engine)

        for mode in ModesTypes:
            modeName = mode.name; modeId = mode.value
            if not Modes.query.filter_by(mode_name=modeName).first():
                db.session.add(Modes(modeId, modeName))
                db.session.commit()

    def resetAPI_Auth():
        if current_user and current_user.is_authenticated:
            current_user.fitbit_authorized = False
            current_user.spotify_authorized = False
            db.session.commit()

    resetAPI_Auth()

    @login_manager.user_loader
    def user_loader(user_id):
        """Given *user_id*, return the associated User object.
        :param unicode user_id: user_id (email) user to retrieve
        """
        return User.query.get(user_id)

    def login_required(): # role='ANY'
        def wrapper(fn):
            @wraps(fn)
            def decorated_view(*args, **kwargs):
                if not current_user.is_authenticated:
                    return app.login_manager.unauthorized()
                # if (current_user.role != role) and (role != 'ANY'):
                #     return abort(403)
                return fn(*args, **kwargs)
            return decorated_view
        return wrapper
    
    def spotify_and_fitbit_authorized_required(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return app.login_manager.unauthorized()
            if not current_user.fitbit_authorized:
                # Redirect to the Fitbit authorization page
                return redirect(url_for('user_authorize_fitbit'))
            if not current_user.spotify_authorized:
                # Redirect to the Spotify authorization page
                return redirect(url_for('user_authorize_spotify'))
            
            return fn(*args, **kwargs)
        
        return decorated_view

    # TODO remove me
    @app.route('/checkSecrets',)
    def checkSecrets():
        return str(getSecret('FITBIT_CLIENT_ID')) + ' isRunningInCloud: ' + str(isRunningInCloud())

    @app.route('/about')
    @login_required()
    def about():
        return render_template('pages/about.html')
   
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        form = LoginForm()
        guest_login_clicked = False
        if form.validate_on_submit():
            if request.form.get('guest_login'):
                guest_login_clicked = True
                user = User.query.filter_by(username=getSecret('GUEST_USERNAME')).first()
                login_user(user, remember=True)
                return redirect(url_for('home'))
            else:
                user = User.query.filter_by(username=form.username.data).first()
                if user and user.password == form.password.data:
                    login_user(user, remember=True)
                    resetAPI_Auth() 
                    return redirect(url_for('home'))
                else:
                    flash('Login unsuccessful. Please check email and password', 'danger')
        return render_template('forms/login.html', title='Login', form=form, guest_login_clicked=guest_login_clicked)

    @app.route("/logout", methods=["POST"])
    def logout():
        user = current_user
        user.authenticated = False
        db.session.add(user)
        db.session.commit()
        logout_user()
        return redirect(url_for('home'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        form = RegisterForm()
        if form.validate_on_submit():
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Congratulations, you are now a registered user!')
            login_user(user)
            return redirect(url_for('home'))
        else:
            print(form.errors)
        return render_template('forms/register.html', title='Register', form=form)

    @app.route('/forgot')
    def forgot():
        form = ForgotForm(request.form)
        return render_template('forms/forgot.html', form=form)

    @app.errorhandler(500)
    def internal_error(error):
        #db_session.rollback()
        return render_template('errors/500.html'), 500
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    

    # ============= adding in fitbit API data handler  =============
    fitbit_API = Fitbit_API(db)
    setattr(app, 'fitbit_API', fitbit_API)
    fitbit_API.add_routes(app, db, spotify_and_fitbit_authorized_required)
    # ============= spotify API data handler ===========
    spotify_API = Spotify_API(db)
    setattr(app, 'spotify_API', spotify_API)
    spotify_API.add_routes(app, db, spotify_and_fitbit_authorized_required)
    # ============= oura API data handler ===========
    oura_API = Oura_API()
    setattr(app, 'oura_API', oura_API)
    oura_API.add_routes(app, db)
    # ============= dash graphs ===========
    dashApp = add_dash_routes(app, db, spotify_and_fitbit_authorized_required)

    @app.route('/')
    def home():
        return render_template('pages/home.html')
    
    @app.route('/selectPlaylist', methods=['GET', 'POST'])
    @spotify_and_fitbit_authorized_required
    def selectPlaylist():
        DEBUG_SLEEP_MODE = 1
        form = SelectPlaylistsForm()
        usedPlaylists = PlaylistsForMode.query.filter_by(mode_id=DEBUG_SLEEP_MODE, user_id=current_user.id).all()
        usedPlayIds = [playlist.playlist_id for playlist in usedPlaylists]
        playlists = spotify_API.userPlaylists()
        if usedPlayIds:
            usedPlaylists = Playlist.query.filter(Playlist.playlist_id.in_(usedPlayIds)).filter_by( user_id=current_user.id).all()
        new_plays = []
        if request.method == 'POST':
            sql_addingPlaylists = []; sql_newPlays = []
            new_plays = request.form.getlist('selected_playlists') # must match the name of input checkbox that is toggle as the user selects playlists
            usedPlaylists = PlaylistsForMode.query.filter_by(mode_id=DEBUG_SLEEP_MODE, user_id=current_user.id).all()
            new_plays = [ast.literal_eval(p.strip()) for p in new_plays] # in html a dictionary is built as a string and must be converted
            new_play_ids = [p['playlist_id'] for p in new_plays]
            sql_play_ids = [p.playlist_id for p in Playlist.query.filter_by(user_id=current_user.id).all()]
            for playlist_dict in new_plays:
                if playlist_dict['playlist_id'] not in sql_play_ids:
                    sql_addingPlaylists.append(Playlist(user_id=current_user.id, playlist_id=playlist_dict['playlist_id'], playlist_name=playlist_dict['playlist_name'], playlist_image_url=playlist_dict['playlist_image']))
                if playlist_dict['playlist_id'] not in usedPlayIds:
                    sql_newPlays.append(PlaylistsForMode(mode_id=DEBUG_SLEEP_MODE, user_id=current_user.id, playlist_id=playlist_dict['playlist_id']))
            for playlist in usedPlaylists:
                if playlist.playlist_id not in new_play_ids:
                    db.session.delete(playlist)
            db.session.add_all(sql_addingPlaylists)
            db.session.add_all(sql_newPlays)
            db.session.commit()
        for playlist in playlists:
            if request.method == 'POST' and playlist['id'] in new_play_ids:
                playlist['selected'] = True
            elif request.method == 'GET' and playlist['id'] in usedPlayIds:
                playlist['selected'] = True
        return render_template('forms/selectPlaylist.html', form=form, playlists=playlists)
    
    @app.route('/dashboard', methods=['GET', 'POST'])
    @spotify_and_fitbit_authorized_required
    def dashboard():
        modes = ModesTypes
        modesData = [{'id': mode.value, 'name': mode.name} for mode in modes]
        form = SelectPlaylistsForm()    
        form_mode_id = form.mode.data
        # PlaylistsForMode.query.delete()
        playlists = spotify_API.userPlaylists()
        if request.method == 'POST':
            if form.validate_on_submit():
                new_plays = []
                sql_addingPlaylists = []; sql_newPlays = []
                new_plays = request.form.getlist('selected_playlists') # must match the name of input checkbox that is toggle as the user selects playlists
                # print(new_plays)
                usedPlaylists = PlaylistsForMode.query.filter_by(mode_id=form_mode_id, user_id=current_user.id).all()
                usedPlayIds = [playlist.playlist_id for playlist in usedPlaylists]
                new_plays = [ast.literal_eval(p.strip()) for p in new_plays] # in html a dictionary is built as a string and must be converted
                new_play_ids = [p['playlist_id'] for p in new_plays]
                # print("POST", form_mode_id, "new_plays", [p['playlist_name'] for p in new_plays])
                sql_play_ids = [p.playlist_id for p in Playlist.query.filter_by(user_id=current_user.id).all()]
                for playlist_dict in new_plays:
                    if playlist_dict['playlist_id'] not in sql_play_ids:
                        sql_addingPlaylists.append(Playlist(user_id=current_user.id, playlist_id=playlist_dict['playlist_id'], playlist_name=playlist_dict['playlist_name'], playlist_image_url=playlist_dict['playlist_image']))
                    if playlist_dict['playlist_id'] not in usedPlayIds:
                        sql_newPlays.append(PlaylistsForMode(mode_id=form_mode_id, user_id=current_user.id, playlist_id=playlist_dict['playlist_id']))
                for playlist in usedPlaylists:
                    if playlist.playlist_id not in new_play_ids:
                        db.session.delete(playlist)
                # print("Adding playlists: ", sql_addingPlaylists, "Adding new plays: ", sql_newPlays)
                db.session.add_all(sql_addingPlaylists)
                db.session.add_all(sql_newPlays)
                db.session.commit()
                for playlist in playlists:
                    if playlist['id'] in new_play_ids:
                        playlist['selected'].append(str(form_mode_id))
        allSelectedPlaylists = PlaylistsForMode.query.filter_by(user_id=current_user.id).all()
        allSelectedPlaylist_ids = {mode['id'] : [playlist.playlist_id for playlist in allSelectedPlaylists if playlist.mode_id == mode['id']] for mode in modesData}
        for modes in modesData:
            mode_id = modes['id']
            for playlist in playlists:
                if playlist['id'] in allSelectedPlaylist_ids[mode_id]:
                    playlist['selected'].append(str(mode_id)) # TODO still add duplicates add duplicates
        # print("allSelectedPlaylist_ids: ", allSelectedPlaylist_ids, "\n", "playlists: ", playlists)
        return render_template('pages/dashboard.html', mode_id=form_mode_id, modes=modesData, form=form, playlists=playlists)
    
    if not app.debug:
        file_handler = FileHandler('error.log')
        file_handler.setFormatter(
            Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
        )
        app.logger.setLevel(logging.INFO)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.info('errors')

    return app