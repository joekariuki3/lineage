# models.py
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from time import time
import jwt

db = SQLAlchemy()


class Family(db.Model):
    """Class representing a family in the application."""
    __tablename__ = 'families'

    family_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    # Relationships
    users = db.relationship('User', back_populates='families')
    events = db.relationship('Event', cascade="all,delete", back_populates='family')
    members = db.relationship('Member', cascade="all,delete-orphan", back_populates='family')
    links = db.relationship('Link', cascade="all,delete-orphan", back_populates='family')

class Link(db.Model):
    """Class representing a link in the application."""
    __tablename__ = 'links'

    link_id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(500), nullable=True)

     # Foreign Key
    family_id = db.Column(db.Integer, db.ForeignKey('families.family_id'), nullable=False)

    # Relationships
    family = db.relationship('Family', back_populates='links')


class Member(db.Model):
    """Class representing a family member in the application."""
    __tablename__ = 'members'

    member_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    birthdate = db.Column(db.Date)
    deathdate = db.Column(db.Date)
    gender = db.Column(db.String(10))
    root = db.Column(db.Boolean)
    alive = db.Column(db.Boolean)
    mother = db.Column(db.Integer, nullable=True)
    father = db.Column(db.Integer, nullable=True)


    # Foreign Keys
    family_id = db.Column(db.Integer, db.ForeignKey('families.family_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)

    # Relationships
    family = db.relationship('Family', back_populates='members')
    relationships1 = db.relationship('Relationship', foreign_keys="[Relationship.member_id_1]", cascade="all, delete-orphan", back_populates='member1')
    relationships2 = db.relationship('Relationship', foreign_keys="[Relationship.member_id_2]", cascade="all, delete-orphan", back_populates='member2')


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

class Event(db.Model):
    """Class representing a family event in the application."""
    __tablename__ = 'events'

    event_id = db.Column(db.Integer, primary_key=True)
    event_date = db.Column(db.DateTime, nullable=False)
    event_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    description = db.Column(db.String(100))

    # Foreign Key
    family_id = db.Column(db.Integer, db.ForeignKey('families.family_id'), nullable=False)

    # Relationships
    family = db.relationship('Family', back_populates='events')

class Relationship(db.Model):
    """Class representing relationships between family members."""
    __tablename__ = 'relationships'

    relationship_id = db.Column(db.Integer, primary_key=True)
    relationship_type = db.Column(db.String(20), nullable=False)

   # Foreign Keys
    member_id_1 = db.Column(db.Integer, db.ForeignKey('members.member_id', name='fk_member_id_1'), nullable=False)
    member_id_2 = db.Column(db.Integer, db.ForeignKey('members.member_id', name='fk_member_id_2'), nullable=False)

    # Relationships
    member1 = db.relationship('Member', foreign_keys=[member_id_1], back_populates='relationships1')
    member2 = db.relationship('Member', foreign_keys=[member_id_2], back_populates='relationships2')

