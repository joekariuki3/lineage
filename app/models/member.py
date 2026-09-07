from datetime import date
from typing import Any

from flask_login import current_user
from sqlalchemy.orm import Mapped

from app.extensions import db
from app.utils.constants import Gender


class Member(db.Model):
    """Represents a Member entity in the family tree database."""

    __tablename__ = "members"

    # Personal Information
    member_id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    first_name: Mapped[str] = db.Column(db.String(50), nullable=False)
    last_name: Mapped[str] = db.Column(db.String(50), nullable=False)
    gender: Mapped[Gender] = db.Column(db.String(10))
    birthdate: Mapped[date] = db.Column(db.Date)
    deathdate: Mapped[date | None] = db.Column(db.Date)
    alive: Mapped[bool] = db.Column(db.Boolean, default=True)

    # Family Tree Structure
    root: Mapped[bool] = db.Column(db.Boolean, default=False)

    # Foreign Keys
    mother: Mapped[int | None] = db.Column(
        db.Integer, db.ForeignKey("members.member_id"), nullable=True
    )
    father: Mapped[int | None] = db.Column(
        db.Integer, db.ForeignKey("members.member_id"), nullable=True
    )
    family_id: Mapped[int] = db.Column(
        db.Integer, db.ForeignKey("families.family_id"), nullable=False
    )
    user_id: Mapped[int | None] = db.Column(
        db.Integer, db.ForeignKey("users.user_id"), nullable=True
    )

    # Relationship
    family = db.relationship("Family", back_populates="members")

    # Relationship References
    # initiated_relationships
    relationships1 = db.relationship(
        "Relationship",
        foreign_keys="[Relationship.member_id_1]",
        cascade="all, delete-orphan",
        back_populates="member1",
    )
    # received_relationships
    relationships2 = db.relationship(
        "Relationship",
        foreign_keys="[Relationship.member_id_2]",
        cascade="all, delete-orphan",
        back_populates="member2",
    )

    def __init__(
        self,
        first_name: str,
        last_name: str,
        family_id: int,
        gender: Gender,
        birthdate: date | None = None,
        deathdate: date | None = None,
        alive: bool | None = None,
        root: bool = False,
        mother: int | None = None,
        father: int | None = None,
        user_id: int | None = None,
    ) -> None:
        """Initialize a new Member instance.

        Args:
            first_name: Member's first name
            last_name: Member's last name
            family_id: ID of the family this member belongs to
            gender: Member's gender (from Gender enum)
            birthdate: Member's date of birth
            deathdate: Member's date of death (if applicable)
            alive: Whether the member is alive (defaults to True if no deathdate, False if deathdate provided)
            root: Whether this is a root member in the family tree
            mother: ID of the member's mother (if known)
            father: ID of the member's father (if known)
            user_id: Associated user ID (if any)
        """
        self.first_name = first_name
        self.last_name = last_name
        self.family_id = family_id
        self.gender = gender
        self.birthdate = birthdate
        self.deathdate = deathdate
        self.alive = False if deathdate else True if alive is None else alive
        self.root = root
        self.mother = mother
        self.father = father
        self.user_id = user_id

        self.validate()

    @property
    def full_name(self) -> str:
        """Returns the member's full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self) -> int | None:
        """Calculates the member's current age or age at death."""
        if not self.birthdate:
            return None
        end_date = self.deathdate if self.deathdate else date.today()
        if end_date < self.birthdate:
            raise ValueError("Death date cannot be before birth date")
        return (
            end_date.year
            - self.birthdate.year
            - (
                (end_date.month, end_date.day)
                < (self.birthdate.month, self.birthdate.day)
            )
        )

    def validate(self) -> None:
        """Validates the member data consistency."""
        if self.deathdate and self.alive:
            raise ValueError("Member cannot be alive if death date is set")

        if self.deathdate and self.birthdate and self.deathdate < self.birthdate:
            raise ValueError("Death date cannot be before birth date")

        if self.birthdate and self.birthdate > date.today():
            raise ValueError("Birth date cannot be in the future")

        if self.gender and self.gender not in [g.value for g in Gender]:
            raise ValueError(f"Invalid gender value: {self.gender}")

        # Validate parent-child relationship
        if self.father and self.mother and self.father == self.mother:
            raise ValueError(
                "Child Member cannot have the same Person as father and mother"
            )

        if self.father and self.mother:
            father = db.session.get(Member, self.father)
            mother = db.session.get(Member, self.mother)
            if self.age > father.age:
                raise ValueError(
                    f"Child {self.full_name}, of Birth-date:{self.birthdate} and Age:{self.age} cannot be\n"
                    f"older than Father: {father.full_name}, of Birth-date:{father.birthdate}\n"
                    f"and Age:{father.age}"
                )
            if self.age > mother.age:
                raise ValueError(
                    f"Child {self.full_name}, of Birth-date:{self.birthdate} and Age:{self.age} cannot be\n"
                    f"older than Mother: {mother.full_name}, of Birth-date:{mother.birthdate}\n"
                    f"and Age:{mother.age}"
                )

    def to_dict(self, access_level: str = "family") -> dict[str, Any]:
        """
        Converts the member instance to a dictionary representation based on access level.

        Args:
            access_level (str): Level of detail to include in the output
                'basic': Only non-sensitive public information
                'family': Information visible to family members
                'admin': Full information including sensitive data

        Returns:
            Dict[str, Any]: Dictionary containing member data based on access level
        """
        # Basic information available to all authenticated users
        basic_data = {
            "member_id": self.member_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
        }

        # Check if the current user has family access
        has_family_access = current_user.is_authenticated and (
            self.family_id in [family.family_id for family in current_user.families]
        )

        # Check if the current user is admin
        # is_admin = current_user.is_authenticated and current_user.is_admin

        if access_level == "basic":
            return basic_data

        if access_level == "family" and has_family_access:
            family_data = {
                **basic_data,
                "gender": self.gender,
                "birthdate": self.birthdate,
                "age": self.age,
                "alive": self.alive,
                "root": self.root,
                "family_id": self.family_id,
            }
            # Only include death date if the person is deceased
            if not self.alive and self.deathdate:
                family_data["deathdate"] = self.deathdate
            return family_data
        #
        # if access_level == 'admin' and is_admin:
        #     return {
        #         **basic_data,
        #         'gender': self.gender,
        #         'birthdate': self.birthdate,
        #         'deathdate': self.deathdate,
        #         'age': self.age,
        #         'alive': self.alive,
        #         'root': self.root,
        #         'mother': self.mother,
        #         'father': self.father,
        #         'family_id': self.family_id,
        #         'user_id': self.user_id
        #     }

        # If the requested access level is not authorized, fall back to basic data
        return basic_data
