from . import db

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
