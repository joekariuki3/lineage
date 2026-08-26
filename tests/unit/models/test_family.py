from datetime import datetime

import pytest

from app.models.event import Event
from app.models.family import Family
from app.models.link import Link
from app.models.member import Member
from app.models.user import User
from app.utils.constants import Gender


def test_family_initialization():
    """
    Test the initialization of a Family instance.
    Verifies that attributes are correctly set.
    """
    family = Family(name="Smith Family", user_id=1)
    assert family.name == "Smith Family"
    assert family.user_id == 1


def test_family_initialization_without_user():
    """
    Test the initialization of a Family instance without a user_id.
    Ensures user_id is None if not provided.
    """
    family = Family(name="Smith Family")
    assert family.name == "Smith Family"
    assert family.user_id is None


def test_family_name_max_length_validation():
    """
    Test that Family instance raises a ValueError when the name exceeds MAX_NAME_LENGTH.
    """
    long_name = "A" * (Family.MAX_NAME_LENGTH + 1)
    with pytest.raises(ValueError, match=f"Family name must be between 1 and {Family.MAX_NAME_LENGTH} characters"):
        Family(name=long_name)


def test_family_name_empty_validation():
    """
    Test that Family instance raises a ValueError when the name is empty.
    """
    with pytest.raises(ValueError, match="Family name must be between 1 and 50 characters"):
        Family(name="")


def test_family_relationships(session):
    """
    Test Family relationships with User, Event, Member, and Link models.
    Verifies relationships are established correctly.
    """
    user = User(name="John Doe", email="john.doe@example.com", password="test")
    session.add(user)
    session.commit()

    family = Family(name="Doe Family", user_id=user.user_id)
    session.add(family)
    session.commit()

    event = Event(event_date=datetime(2024, 5, 7, 11, 22), event_name="Family Reunion", family_id=family.family_id)
    member = Member(first_name="Jane", last_name="Doe", family_id=family.family_id, gender=Gender.MALE.value)
    link = Link(link="https://joelmhoho.com", family_id=family.family_id)

    session.add_all([event, member, link])
    session.commit()

    assert family.users is not None
    assert len(family.events) == 1
    assert family.events[0].event_name == "Family Reunion"
    assert len(family.members) == 1
    assert family.members[0].first_name == "Jane"
    assert len(family.links) == 1
    assert family.links[0].link == "https://joelmhoho.com"


def test_family_cascade_delete_relationships(session):
    """
    Test cascading deletion for related entities.
    Ensures that deleting a Family instance deletes related Members, Events, and Links.
    """
    family = Family(name="Test Family", user_id=1)
    session.add(family)
    session.commit()

    event = Event(event_date=datetime(2025, 1, 2, 1, 44), event_name="Birthday Party", family_id=family.family_id)
    member = Member(first_name="Test", last_name="Member", family_id=family.family_id, gender=Gender.FEMALE.value)
    link = Link(link="https://joelmuhoho.com", family_id=family.family_id)

    session.add_all([family, event, member, link])
    session.commit()

    session.delete(family)
    session.commit()

    assert session.query(Event).filter_by(family_id=family.family_id).count() == 0
    assert session.query(Member).filter_by(family_id=family.family_id).count() == 0
    assert session.query(Link).filter_by(family_id=family.family_id).count() == 0