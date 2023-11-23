# models.py
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()



class Family(db.Model):
    """Class representing a family in the application."""
    __tablename__ = 'families'

    family_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    # Relationships
    users = db.relationship('User', back_populates='families')
    events = db.relationship('Event', back_populates='family')
    members = db.relationship('Member', back_populates='family')

class Member(db.Model):
    """Class representing a family member in the application."""
    __tablename__ = 'members'

    member_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    birthdate = db.Column(db.Date)
    gender = db.Column(db.String(10))
    root = db.Column(db.Boolean)


    # Foreign Keys
    family_id = db.Column(db.Integer, db.ForeignKey('families.family_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)

    # Relationships
    family = db.relationship('Family', back_populates='members')

class User(db.Model, UserMixin):
    """Class representing a user in the application."""
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(2500), nullable=False)
    families = db.relationship('Family', back_populates='users')

    def set_password(self, user_password):
        self.password = generate_password_hash(user_password)

    def check_password(self, user_password):
        return check_password_hash(self.password, user_password)

    def get_id(self):
           return (self.user_id)

class Event(db.Model):
    """Class representing a family event in the application."""
    __tablename__ = 'events'

    event_id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(100), nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    event_time = db.Column(db.Time)
    location = db.Column(db.String(100))

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
    member_id_1 = db.Column(db.Integer, db.ForeignKey('members.member_id'), nullable=False)
    member_id_2 = db.Column(db.Integer, db.ForeignKey('members.member_id'), nullable=False)