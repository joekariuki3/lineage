from app.extensions import db
from sqlalchemy.orm import Mapped
from .member import Member
from app.utils.constants import RelationType


class Relationship(db.Model):
    """Class representing relationships between family members."""

    __tablename__ = "relationships"

    relationship_id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    relationship_type: Mapped[str] = db.Column(db.String(20), nullable=False)

    # Foreign Keys
    member_id_1: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("members.member_id", name="fk_member_id_1"),
        nullable=False,
    )
    member_id_2: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("members.member_id", name="fk_member_id_2"),
        nullable=False,
    )

    # Relationships
    member1: Mapped[Member] = db.relationship(
        "Member", foreign_keys=[member_id_1], back_populates="relationships1"
    )
    member2: Mapped[Member] = db.relationship(
        "Member", foreign_keys=[member_id_2], back_populates="relationships2"
    )

    def __init__(
        self, relationship_type: RelationType, member_id_1: int, member_id_2: int
    ) -> None:
        """
        Initialize a new relationship between family members.

        Args:
            relationship_type: Type of relationship from RelationType enum
            member_id_1: ID of the first member
            member_id_2: ID of the second member

        Raises:
            TypeError: If relationship_type is not a RelationType enum
        """
        if not isinstance(relationship_type, RelationType):
            raise TypeError("relationship_type must be a RelationType enum")

        self.relationship_type = relationship_type.value
        self.member_id_1 = member_id_1
        self.member_id_2 = member_id_2

    def validate(self) -> None:
        """
        Validate the relationship.

        Raises:
            ValueError: If the relationship is invalid
        """
        if self.member_id_1 == self.member_id_2:
            raise ValueError("A member cannot have a relationship with themselves")

        if self.relationship_type == RelationType.PARENT.value:
            parent = db.session.get(Member, self.member_id_1)
            child = db.session.get(Member, self.member_id_2)

            if (
                parent
                and child
                and parent.birthdate
                and child.birthdate
                and parent.birthdate >= child.birthdate
            ):
                raise ValueError("Parent must be older than child")
