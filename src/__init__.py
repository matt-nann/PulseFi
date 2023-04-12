import os
from dotenv import load_dotenv

FLASK_PORT = 8080
CLOUD_URL = 'https://pulse-fi.herokuapp.com'

load_dotenv()

def getSecret(secret):
    return os.environ.get(secret)

def isRunningInCloud():
    return os.environ.get('RUNNING') == 'cloud'

def baseUrl():
    if isRunningInCloud():
        return CLOUD_URL
    else:
        return 'http://127.0.0.1:'+str(FLASK_PORT)