from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(120), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(30))
    def __init__(self, username=None, email=None):
        self.username = username
        self.email = email
    def set_password(self, password):
        self.password = password
    def check_password(self, password):
        return self.password == password
    def is_active(self):
        return True
