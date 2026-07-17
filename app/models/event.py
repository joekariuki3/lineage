from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Mapped
from app.extensions import db


class Event(db.Model):
    """
    Represents a family event in the application.

    This class models events associated with families, including details like date,
    name, location, and description. Each event belongs to a specific family.

    Attributes:
        event_id: Unique identifier for the event
        event_date: Date and time when the event occurs
        event_name: Name/title of the event
        location: Optional location where the event takes place
        description: Optional description of the event
        family_id: ID of the family this event belongs to
        family: Relationship to the associated Family model
    """

    # Field length constants
    NAME_LENGTH: int = 100
    LOCATION_LENGTH: int = 100
    DESCRIPTION_LENGTH: int = 100

    __tablename__ = "events"

    # Primary key
    event_id: Mapped[int] = db.Column(db.Integer, primary_key=True)

    # Required fields
    event_date: Mapped[datetime] = db.Column(db.DateTime, nullable=False)
    event_name: Mapped[str] = db.Column(db.String(NAME_LENGTH), nullable=False)

    # Optional fields
    location: Mapped[Optional[str]] = db.Column(db.String(LOCATION_LENGTH))
    description: Mapped[Optional[str]] = db.Column(db.String(DESCRIPTION_LENGTH))

    # Foreign key
    family_id: Mapped[int] = db.Column(
        db.Integer, db.ForeignKey("families.family_id"), nullable=False
    )

    # Relationships
    family = db.relationship("Family", back_populates="events")

    def __init__(
        self,
        event_date: datetime,
        event_name: str,
        family_id: int,
        location: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        """
        Initialize a new Event instance.

        Args:
            event_date: Date and time of the event
            event_name: Name of the event
            family_id: ID of the family this event belongs to
            location: Optional location of the event
            description: Optional description of the event
        """
        self.event_date = event_date
        self.event_name = event_name
        self.family_id = family_id
        self.location = location
        self.description = description

    def __repr__(self) -> str:
        """Return string representation of the event."""
        return f"Event(name='{self.event_name}', date={self.event_date}, family_id={self.family_id})"
