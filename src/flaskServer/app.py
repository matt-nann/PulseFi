import os
from flask import Flask, render_template, request, flash, redirect, url_for, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import logging
from functools import wraps
from logging import Formatter, FileHandler

from .forms import *
from .models import User, db
from __init__ import getSecret

from data.callbacks import FitbitAuth

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
    with app.app_context():
        db.create_all()

    # app.config.from_object('config')

    # # Automatically tear down SQLAlchemy.
    # @app.teardown_request
    # def shutdown_session(exception=None):
    #     db_session.remove()

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

    #----------------------------------------------------------------------------#
    # Controllers.
    #----------------------------------------------------------------------------#

    @app.route('/')
    def home():
        return render_template('pages/placeholder.home.html')
    
    @app.route('/checkSecrets',)
    def checkSecrets():
        return str(getSecret('FITBIT_CLIENT_ID'))

    @app.route('/about')
    @login_required()
    def about():
        return render_template('pages/placeholder.about.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.password == form.password.data:
                login_user(user, remember=True)
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
    fitbitAPI = FitbitAuth()
    fitbitAPI.add_routes(app)

    # ============= dash


    
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