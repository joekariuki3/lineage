from . import db

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

    def __init__(self, event_date, event_name, family_id, event_location = None, event_description = None):
        self.event_date = event_date
        self.event_name = event_name
        self.family_id = family_id
        self.location = event_location
        self.description = event_description
