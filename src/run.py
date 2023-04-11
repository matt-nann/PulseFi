from flaskServer.app import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0',port=8080,threaded=True)


# # create a basic flask app
# from flask import Flask
# app = Flask(__name__)

# @app.route('/')
# def hello_world():
#     return 'Hello, World!'

# if __name__ == '__main__':
#     app.run()