import os
from dotenv import load_dotenv

FLASK_PORT = 8080

load_dotenv()

def getSecret(secret):
    return os.environ.get(secret)

def isRunningInCloud():
    return os.environ.get('RUNNING') == 'cloud'