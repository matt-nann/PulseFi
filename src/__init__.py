import os
from dotenv import load_dotenv

load_dotenv()

def getSecret(secret):
    return os.environ.get(secret)