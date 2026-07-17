from app.extensions import db
from sqlalchemy.orm import Mapped


class Link(db.Model):
    """
    Represents a shareable link entity in the application.
    Links are associated with families and contain tokens or URLs for sharing purposes.
    """

    # Configuration
    __tablename__ = "links"

    # Field length constraints
    MAX_URL_LENGTH: int = 500

    # Primary key
    link_id: Mapped[int] = db.Column(
        db.Integer, primary_key=True, comment="Unique identifier for the link"
    )

    # Basic attributes
    link: Mapped[str] = db.Column(
        db.String(MAX_URL_LENGTH),
        nullable=False,
        comment="URL or token string for sharing",
    )

    # Foreign keys
    family_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("families.family_id"),
        nullable=False,
        comment="Reference to associated family",
    )

    # Relationships
    family = db.relationship("Family", back_populates="links")

    def __init__(self, link: str, family_id: int, family=None) -> None:
        """
        Initialize a new Link instance.

        Args:
            link: The URL or token string
            family_id: ID of the associated family
            family: Optional Family instance for relationship
        """
        if len(link) > self.MAX_URL_LENGTH:
            raise ValueError(f"Link URL cannot exceed {self.MAX_URL_LENGTH} characters")
        self.link = link
        self.family_id = family_id
        if family:
            self.family = family

    def __repr__(self) -> str:
        """String representation of the Link instance."""
        return f"<Link id={self.link_id} family_id={self.family_id}>"
