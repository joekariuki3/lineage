from . import db

class Link(db.Model):
    """Class representing a link in the application."""
    __tablename__ = 'links'

    link_id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(500), nullable=True)

     # Foreign Key
    family_id = db.Column(db.Integer, db.ForeignKey('families.family_id'), nullable=False)

    # Relationships
    family = db.relationship('Family', back_populates='links')

