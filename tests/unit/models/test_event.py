from datetime import datetime

from app.models.event import Event


def test_event_initialization():
    """
    Test the initialization of an Event instance.
    Verifies that attributes are correctly set.
    """
    event_date = datetime(2023, 10, 25, 15, 0)
    event = Event(event_date=event_date, event_name="Family Reunion", family_id=1, location="Park", description="Annual gathering")

    assert event.event_date == event_date
    assert event.event_name == "Family Reunion"
    assert event.family_id == 1
    assert event.location == "Park"
    assert event.description == "Annual gathering"


def test_event_without_optional_fields():
    """
    Test the initialization of an Event instance without optional fields.
    Verifies that optional attributes are None.
    """
    event_date = datetime(2023, 12, 31, 20, 0)
    event = Event(event_date=event_date, event_name="New Year Party", family_id=2)

    assert event.event_date == event_date
    assert event.event_name == "New Year Party"
    assert event.family_id == 2
    assert event.location is None
    assert event.description is None


def test_event_representation():
    """
    Test the string representation of an Event instance.
    Ensures the representation is formatted correctly.
    """
    event_date = datetime(2023, 5, 10, 10, 30)
    event = Event(event_date=event_date, event_name="Birthday Party", family_id=3)
    expected_repr = "Event(name='Birthday Party', date=2023-05-10 10:30:00, family_id=3)"

    assert repr(event) == expected_repr
