import os
from src import getSecret, isRunningInCloud
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    DEBUG = True
    # Secret key for session management. You can generate random strings here: https://randomkeygen.com/
    SECRET_KEY = "o'lEd~n48G[3&@XVF2*]u1`VPF7P%I%,:OA@wuI`.5|%$4neB>h{q=S1N<R5AKL"

    if isRunningInCloud():
        SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    else:
        SQL_username = str(getSecret('SQL_User'))
        SQL_password = str(getSecret('SQL_Password'))
        SQL_host = str(getSecret('SQL_Host'))
        SQL_port = str(getSecret('SQL_Port'))
        SQL_database = str(getSecret('SQL_Database'))
        # Connect to the database
        SQLALCHEMY_DATABASE_URI = 'postgresql://' + SQL_username + ':' + SQL_password + '@' + SQL_host + ':' + SQL_port + '/' + SQL_database
        # 'sqlite:///' + os.path.join(basedir, 'database.db')

    # # Secret key for session management. You can generate random strings here:
    # # https://randomkeygen.com/
    # SECRET_KEY = "o'lEd~n48G[3&@XVF2*]u1`VPF7P%I%,:OA@wuI`.5|%$4neB>h{q=S1N<R5AKL"
    # # Connect to the database
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.db')
