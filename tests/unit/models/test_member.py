from datetime import date

import pytest

from app.models.member import Gender, Member


def test_member_initialization():
    """
    Test the initialization of a Member instance.
    Verifies that attributes are correctly set.
    """
    member = Member(
        first_name="John",
        last_name="Doe",
        family_id=1,
        gender=Gender.MALE.value,
        birthdate=date(1990, 1, 1),
        alive=True,
        root=True,
        mother=None,
        father=None,
        user_id=2
    )
    assert member.first_name == "John"
    assert member.last_name == "Doe"
    assert member.family_id == 1
    assert member.gender == Gender.MALE.value
    assert member.birthdate == date(1990, 1, 1)
    assert member.alive is True
    assert member.root is True
    assert member.mother is None
    assert member.father is None
    assert member.user_id == 2

def test_member_full_name():
    """
    Test the full_name property of a Member instance.
    Verifies that the full name is correctly generated.
    """
    member = Member(first_name="Jane", last_name="Smith", family_id=1, gender=Gender.MALE.value)
    assert member.full_name == "Jane Smith"

def test_member_age_calculation():
    """
    Test the age calculation of a Member instance.
    Verifies that the age is calculated correctly based on birthdate and deathdate.
    """
    member_alive = Member(
        first_name="John",
        last_name="Doe",
        family_id=1,
        birthdate=date(1990, 1, 1),
        gender=Gender.FEMALE.value
    )
    assert member_alive.age == date.today().year - 1990

    member_deceased = Member(
        first_name="Jane",
        last_name="Doe",
        family_id=1,
        birthdate=date(1980, 1, 1),
        deathdate=date(2020, 1, 1),
        gender=Gender.MALE.value
    )
    assert member_deceased.age == 40

def test_member_validation_birthdate_in_future():
    """
    Test that a ValueError is raised if a member's birthdate is set in the future.
    """
    future_date = date.today().replace(year=date.today().year + 1)
    with pytest.raises(ValueError, match="Birth date cannot be in the future"):
        Member(first_name="Jane", last_name="Doe", family_id=1, birthdate=future_date, gender=Gender.OTHER.value)

def test_member_validation_death_before_birth():
    """
    Test that a ValueError is raised if a member's deathdate is before their birthdate.
    """
    with pytest.raises(ValueError, match="Death date cannot be before birth date"):
        Member(
            first_name="John",
            last_name="Doe",
            family_id=1,
            birthdate=date(1990, 1, 1),
            deathdate=date(1989, 12, 31),
            gender=Gender.FEMALE.value
        )
