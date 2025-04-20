from . import db

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
    member2 = db.relationship('Member', foreign_keys=[member_id_2],  back_populates='relationships2')
