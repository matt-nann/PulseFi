import os
from flask import Flask, render_template, request, flash, redirect, url_for, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
import logging
from functools import wraps
from logging import Formatter, FileHandler
import requests
import pandas as pd

from .forms import *
from .models import User, db
from src import getSecret, isRunningInCloud, baseUrl
from src.APIs.fitbitData import Fitbit_API
from src.APIs.spotifyData import Spotify_API
from src.APIs.ouraData import Oura_API
from src.dashboard import add_dash_routes

def create_app():

    #----------------------------------------------------------------------------#
    # App Config.
    #----------------------------------------------------------------------------#

    app = Flask(__name__)
    # Grabs the folder where the script runs.
    basedir = os.path.abspath(os.path.dirname(__file__))

    # Enable debug mode.
    app.config.DEBUG = True
    # Secret key for session management. You can generate random strings here:
    # https://randomkeygen.com/
    app.config['SECRET_KEY'] = "o'lEd~n48G[3&@XVF2*]u1`VPF7P%I%,:OA@wuI`.5|%$4neB>h{q=S1N<R5AKL"
    # Connect to the database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')

    login_manager = LoginManager()
    login_manager.init_app(app)

    db.init_app(app)
    migrate = Migrate(app, db)
    with app.app_context():
        db.create_all()

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

    @app.route('/')
    def home():
        return render_template('pages/home.html')

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
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.password == form.password.data:
                login_user(user, remember=True)
                resetAPI_Auth() 
                return redirect(url_for('home'))
            else:
                flash('Login unsuccessful. Please check email and password', 'danger')
        return render_template('forms/login.html', title='Login', form=form)

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
    fitbit_API = Fitbit_API()
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

    @app.route('/graph', methods=['GET'])
    @spotify_and_fitbit_authorized_required
    def graph():

        df_heartRate = fitbit_API.heartRateData()
        df_recentlyPlayed = spotify_API.recentlyPlayedData()

        audio_features = spotify_API.getAudioFeatures(df_recentlyPlayed)
        # import plotly.graph_objects as go

        # # create a plotly graph
        # fig = go.Figure()
        # fig.add_trace(go.Scatter(x=df_heartRate['datetime'], y=df_heartRate['bpm'], name='Heart Rate'))
        # # fig.add_trace(go.Scatter(x=df_recentlyPlayed['played_at'], y=df_recentlyPlayed['energy'], name='Energy'))
        # fig.update_layout(title='Heart Rate and Energy', xaxis_title='Date', yaxis_title='Value')

        return audio_features.to_html()
    
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