import os
from flask import Flask
# from dotenv import load_dotenv

# load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'cpsc keys'

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app

def getSecret(secret):
    return os.environ.get(secret)