from . import db

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
