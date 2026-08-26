from datetime import date

import pytest

from app.models.member import Member
from app.models.relationship import Relationship, RelationType
from app.utils.constants import Gender


def test_relationship_initialization():
    """
    Test the initialization of a Relationship instance.
    Verifies that attributes are correctly set.
    """
    relationship = Relationship(
        relationship_type=RelationType.SPOUSE,
        member_id_1=1,
        member_id_2=2
    )

    assert relationship.relationship_type == "spouse"
    assert relationship.member_id_1 == 1
    assert relationship.member_id_2 == 2


def test_relationship_self_relationship_validation():
    """
    Test that a member cannot have a relationship with themselves.
    """
    relationship = Relationship(
        relationship_type=RelationType.SIBLING,
        member_id_1=1,
        member_id_2=1
    )

    with pytest.raises(ValueError, match="A member cannot have a relationship with themselves"):
        relationship.validate()


def test_relationship_parent_child_age_validation(session):
    """
    Test that the parent must be older than the child.
    """
    parent = Member(first_name="John", last_name="Doe", family_id=1, birthdate=date(1980, 1, 1), gender=Gender.FEMALE.value)
    child = Member(first_name="Jane", last_name="Doe", family_id=1, birthdate=date(2005, 1, 1), gender=Gender.FEMALE.value)
    session.add_all([parent, child])
    session.commit()

    relationship = Relationship(
        relationship_type=RelationType.PARENT,
        member_id_1=parent.member_id,
        member_id_2=child.member_id
    )
    relationship.validate()  # Should not raise any exceptions

    child.birthdate = date(1975, 1, 1)  # Change the child's birthdate to an earlier date
    session.commit()

    with pytest.raises(ValueError, match="Parent must be older than child"):
        relationship.validate()


def test_invalid_relationship_type():
    """
    Test that initializing a relationship with an invalid relationship_type raises a TypeError.
    """
    with pytest.raises(TypeError, match="relationship_type must be a RelationType enum"):
        Relationship(
            relationship_type="invalid_type",
            member_id_1=1,
            member_id_2=2
        )