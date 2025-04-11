from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from time import time
import jwt

class User(db.Model, UserMixin):
    """Class representing a user in the application."""
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(2500), nullable=False)
    emailVerify = db.Column(db.Boolean, default=False)
    families = db.relationship('Family', back_populates='users')

    def set_password(self, user_password):
        """change password from string to hash value to store to database"""
        self.password = generate_password_hash(user_password)

    def check_password(self, user_password):
        """check the passed string if matches the hash value stored in the database"""
        return check_password_hash(self.password, user_password)

    def get_id(self):
           """returns an id of a user"""
           return (self.user_id)

    def get_reset_password_token(self, secret, expires_in=600):
        return jwt.encode(
            {'reset_password': self.user_id, 'exp': time() + expires_in},
            secret, algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(secret, token):
        try:
            id = jwt.decode(token, secret,
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return db.session.get(User, id)
