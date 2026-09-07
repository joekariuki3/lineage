
from sqlalchemy.orm import Mapped

from app.extensions import db


class Family(db.Model):
    """
    Represents a family entity in the application with its relationships and attributes.
    Manages family structure and interactions with users, events, members, and links.
    """

    # Configuration
    __tablename__ = "families"

    # Field length constraints
    MAX_NAME_LENGTH: int = 50

    # Primary key
    family_id: Mapped[int] = db.Column(
        db.Integer, primary_key=True, comment="Unique identifier for the family"
    )

    # Basic attributes
    name: Mapped[str] = db.Column(
        db.String(MAX_NAME_LENGTH), nullable=False, comment="Name of the family"
    )

    # Foreign keys
    user_id: Mapped[int | None] = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=True,
        comment="Optional reference to associated user",
    )

    # Relationships with cascading behavior
    users = db.relationship("User", back_populates="families")
    events = db.relationship("Event", cascade="all,delete", back_populates="family")
    members = db.relationship(
        "Member", cascade="all,delete-orphan", back_populates="family"
    )
    links = db.relationship(
        "Link", cascade="all,delete-orphan", back_populates="family"
    )

    def __init__(self, name: str, user_id: int | None = None) -> None:
        """Initialize a new family instance."""
        self.validate_name(name)
        self.name = name
        self.user_id = user_id

    @staticmethod
    def validate_name(name: str) -> None:
        """Validate the family name."""
        if not name or len(name) > Family.MAX_NAME_LENGTH:
            raise ValueError(
                f"Family name must be between 1 and {Family.MAX_NAME_LENGTH} characters"
            )

    def __repr__(self) -> str:
        """Return string representation of the family."""
        return (
            f"Family(id={self.family_id}, name='{self.name}', user_id={self.user_id})"
        )
