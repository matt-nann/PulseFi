from src.flask.app import create_app
from src.data.callbacks import FitbitAuth

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0',port=8080,threaded=True)
